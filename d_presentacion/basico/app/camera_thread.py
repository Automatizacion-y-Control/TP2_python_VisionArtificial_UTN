import time
import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

import config
from detector import ColorDetector
from filters import AntiNoiseFilter

# Suprimir logging verbose de OpenCV (evita spam de ObSensor/RealSense en consola)
try:
    cv2.setLogLevel(0)
except AttributeError:
    pass

# Tamaño máximo para las imágenes enviadas a la UI (evita saturación en el bus de señales)
_DISPLAY_W = 640
_DISPLAY_H = 480


class CameraThread(QThread):
    """
    Captura de video y pipeline completo de visión artificial en hilo secundario.

    Señales:
        frame_ready(QImage)     — Frame BGR anotado para la vista de video en vivo.
        hsv_ready(QImage)       — Representación visual del espacio HSV.
        masks_ready(QImage)     — Panel triple de máscaras binarias (R/V/A).
        stats_updated(dict)     — Estadísticas del frame: pixel counts, fps, color confirmado.
        color_confirmed(str)    — Emitida cuando el color cambia (señal para envío serial).
        error_occurred(str)     — Mensaje de error crítico.
    """

    frame_ready     = pyqtSignal(QImage)
    hsv_ready       = pyqtSignal(QImage)
    masks_ready     = pyqtSignal(QImage)
    stats_updated   = pyqtSignal(dict)
    color_confirmed = pyqtSignal(str)
    error_occurred  = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._camera_index: int = config.CAMERA_INDEX
        self._running: bool = False
        self._detector = ColorDetector()
        self._filter   = AntiNoiseFilter()

    # ------------------------------------------------------------------ #
    # Control externo
    # ------------------------------------------------------------------ #

    def start_capture(self, camera_index: int = 0) -> None:
        if self.isRunning():
            return
        self._camera_index = camera_index
        self._filter.reset()
        self._running = True
        self.start()

    def stop_capture(self) -> None:
        self._running = False
        self.wait(3000)

    def update_filter_thresholds(self, min_pixels: int, stability_frames: int) -> None:
        self._filter.update_thresholds(min_pixels, stability_frames)

    # ------------------------------------------------------------------ #
    # Loop principal
    # ------------------------------------------------------------------ #

    def run(self) -> None:
        # En Windows, MSMF y DirectShow requieren COM inicializado en el hilo que los usa.
        # QThread no lo hace automáticamente → segfault silencioso sin esto.
        _com_initialized = False
        try:
            import ctypes
            hr = ctypes.windll.ole32.CoInitializeEx(None, 0)  # APARTMENTTHREADED
            _com_initialized = hr in (0, 1)  # S_OK o S_FALSE (ya inicializado)
        except Exception:
            pass

        cap = cv2.VideoCapture(self._camera_index, cv2.CAP_MSMF)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

        if not cap.isOpened():
            self.error_occurred.emit(
                f"No se pudo abrir la cámara {self._camera_index}. "
                "Verifique que esté conectada y no esté en uso."
            )
            return

        prev_time = time.perf_counter()

        while self._running:
            ret, frame = cap.read()
            if not ret or frame is None:
                time.sleep(0.01)
                continue

            try:
                hsv, masks, pixel_counts = self._detector.process_frame(frame)
                confirmed_color, should_send, active_candidate = self._filter.filter_detection(pixel_counts)

                now = time.perf_counter()
                fps = 1.0 / max(now - prev_time, 1e-6)
                prev_time = now

                self.stats_updated.emit({
                    **pixel_counts,
                    "fps": fps,
                    "confirmed": confirmed_color,
                    "candidate": active_candidate,
                    "should_send": should_send,
                })

                if should_send:
                    self.color_confirmed.emit(confirmed_color)

                self.frame_ready.emit(self._annotate_frame(frame, confirmed_color, active_candidate, fps))
                self.hsv_ready.emit(self._bgr_to_qimage(cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)))
                self.masks_ready.emit(self._build_masks_panel(masks, pixel_counts))

            except Exception as exc:
                self.error_occurred.emit(str(exc))

        cap.release()

        if _com_initialized:
            try:
                import ctypes
                ctypes.windll.ole32.CoUninitialize()
            except Exception:
                pass

    # ------------------------------------------------------------------ #
    # Helpers de imagen
    # ------------------------------------------------------------------ #

    def _annotate_frame(
        self,
        frame: np.ndarray,
        confirmed: str,
        candidate: str,
        fps: float,
    ) -> QImage:
        out = frame.copy()
        meta = config.COLOR_METADATA.get(confirmed, config.COLOR_METADATA["ninguno"])
        font = cv2.FONT_HERSHEY_SIMPLEX

        # Caja de info semi-transparente
        overlay = out.copy()
        cv2.rectangle(overlay, (8, 8), (305, 120), (8, 14, 22), -1)
        cv2.addWeighted(overlay, 0.72, out, 0.28, 0, out)

        cv2.putText(out, "UTN FRC - TP2  Vision Artificial", (14, 26), font, 0.44, (160, 170, 180), 1)
        cv2.putText(out, f"FPS: {fps:5.1f}", (14, 46), font, 0.46, (0, 212, 255), 1)
        cv2.putText(out, f"Detectado: {candidate.upper()}", (14, 68), font, 0.46, (120, 140, 160), 1)
        cv2.putText(out, f"Estable:   {meta['label']}", (14, 92), font, 0.52, meta["color_bgr"], 2)
        cv2.putText(out, "Legajo 420581", (14, 114), font, 0.36, (70, 90, 110), 1)

        # Indicador circular en esquina superior derecha
        cx = out.shape[1] - 38
        cv2.circle(out, (cx, 36), 27, (5, 10, 18), -1)
        cv2.circle(out, (cx, 36), 25, meta["color_bgr"], -1)

        return self._bgr_to_qimage(out)

    def _bgr_to_qimage(self, bgr: np.ndarray) -> QImage:
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        return QImage(rgb.tobytes(), w, h, ch * w, QImage.Format_RGB888)

    def _build_masks_panel(self, masks: dict, pixel_counts: dict) -> QImage:
        _COLOR_TINTS = {
            "rojo":     np.array([40, 40, 200], dtype=np.uint8),
            "verde":    np.array([40, 200, 60], dtype=np.uint8),
            "amarillo": np.array([40, 200, 200], dtype=np.uint8),
        }
        panels = []
        for color in ("rojo", "verde", "amarillo"):
            small = cv2.resize(masks[color], (213, 160))
            panel = np.zeros((160, 213, 3), dtype=np.uint8)
            # Píxeles activos con tinte de color; fondo muy oscuro
            panel[small > 0] = _COLOR_TINTS[color]
            panel[small == 0] = [12, 18, 26]
            label = f"{color.upper()} {pixel_counts[color]:5d}px"
            cv2.putText(panel, label, (6, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.37,
                        tuple(int(x) for x in _COLOR_TINTS[color]), 1)
            panels.append(panel)

        combined = np.hstack(panels)
        rgb = cv2.cvtColor(combined, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        return QImage(rgb.tobytes(), w, h, ch * w, QImage.Format_RGB888)
