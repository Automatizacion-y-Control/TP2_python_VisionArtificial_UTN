"""
Panel de Control Industrial — TP2 Visión Artificial y Control de Color
UTN FRC | Alumno: Cristian Gonzalo Vera | Legajo: 420581
"""

from __future__ import annotations

import os
import time
from datetime import datetime

import numpy as np
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QPixmap
from PyQt5.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QComboBox,
)

import config
import styles
from camera_thread import CameraThread
from serial_comm import SerialCommunicator


# ══════════════════════════════════════════════════════════════════════
# LED indicador de estado (widget personalizado)
# ══════════════════════════════════════════════════════════════════════

class LedIndicator(QLabel):
    """Círculo de color con efecto de sombra/brillo para indicar estado."""

    _COLORS = {
        "off":       ("#2A3A4E", "#1A2A3E"),
        "connected": ("#00E676", "#004A20"),
        "mock":      ("#FFD600", "#3A2A00"),
        "error":     ("#FF4444", "#4A0808"),
        "link":      ("#00D4FF", "#003845"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(14, 14)
        self._state = "off"
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(10)
        self._shadow.setOffset(0, 0)
        self.setGraphicsEffect(self._shadow)
        self.set_state("off")

    def set_state(self, state: str) -> None:
        self._state = state
        fg, _ = self._COLORS.get(state, self._COLORS["off"])
        self.setStyleSheet(
            f"background-color: {fg}; border-radius: 7px; border: 1px solid rgba(0,0,0,60);"
        )
        color = QColor(fg)
        self._shadow.setColor(color)
        self._shadow.setBlurRadius(12 if state != "off" else 0)


# ══════════════════════════════════════════════════════════════════════
# Ventana principal
# ══════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TP2 — Visión Artificial y Control de Color  |  UTN FRC")
        self.setMinimumSize(1150, 740)
        self.resize(1280, 800)

        # Estado interno
        self._link_active: bool = False
        self._camera_active: bool = False
        self._serial_connected: bool = False
        self._session_start: float = time.time()
        self._detection_counts: dict = {"rojo": 0, "verde": 0, "amarillo": 0}
        self._last_fps: float = 0.0
        self._led_mode: str = "pulso"          # "pulso" | "continuo"
        self._current_confirmed: str = "ninguno"  # último color estable confirmado

        # Componentes core
        self._camera = CameraThread(self)
        self._serial = SerialCommunicator()

        # Timers
        self._heartbeat_timer = QTimer(self)
        self._heartbeat_timer.timeout.connect(self._on_heartbeat)
        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._on_blink_tick)
        self._blink_state: bool = True

        self._build_ui()
        self._connect_signals()
        self._scan_ports()
        self._log("INFO", "Panel de Control Industrial iniciado — UTN FRC TP2.")
        self._log("INFO", "Seleccione puerto COM y cámara, luego presione Conectar.")

    # ------------------------------------------------------------------ #
    # Construcción de la UI
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_header())

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_center_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setSizes([240, 680, 340])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setCollapsible(2, False)
        root_layout.addWidget(splitter, stretch=1)

        root_layout.addWidget(self._build_log_panel())

    # ── Header ─────────────────────────────────────────────────────────

    def _build_header(self) -> QWidget:
        w = QWidget()
        w.setObjectName("w_header")
        w.setFixedHeight(56)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(12)

        # Título
        vlay = QVBoxLayout()
        vlay.setSpacing(0)
        lbl_title = QLabel("PANEL DE CONTROL  ·  VISIÓN ARTIFICIAL")
        lbl_title.setObjectName("lbl_app_title")
        lbl_sub = QLabel("UTN FRC  |  Introducción a la Visión Artificial  |  TP2  |  Legajo 420581")
        lbl_sub.setObjectName("lbl_app_subtitle")
        vlay.addWidget(lbl_title)
        vlay.addWidget(lbl_sub)
        lay.addLayout(vlay)

        lay.addStretch()

        # LED de estado serial
        self.led_status = LedIndicator()
        self.lbl_status_text = QLabel("SIN CONEXIÓN")
        self.lbl_status_text.setObjectName("lbl_section")
        self.lbl_status_text.setAlignment(Qt.AlignVCenter)
        lay.addWidget(self.led_status)
        lay.addWidget(self.lbl_status_text)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFixedHeight(28)
        lay.addWidget(sep)

        # Botón LINK MODE
        self.btn_link = QPushButton("▶  LINK MODE")
        self.btn_link.setObjectName("btn_link")
        self.btn_link.setCheckable(False)
        self.btn_link.clicked.connect(self._toggle_link)
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(0)
        effect.setOffset(0, 0)
        effect.setColor(QColor(styles.ACCENT))
        self.btn_link.setGraphicsEffect(effect)
        self._link_btn_effect = effect
        lay.addWidget(self.btn_link)

        return w

    # ── Panel izquierdo ────────────────────────────────────────────────

    def _build_left_panel(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFixedWidth(252)

        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(10)

        lay.addWidget(self._build_connection_group())
        lay.addWidget(self._build_manual_test_group())
        lay.addWidget(self._build_led_mode_group())
        lay.addWidget(self._build_phase2_group())
        lay.addStretch()

        scroll.setWidget(content)
        return scroll

    def _build_connection_group(self) -> QGroupBox:
        gb = QGroupBox("CONEXIÓN")
        lay = QVBoxLayout(gb)
        lay.setSpacing(8)

        # Puerto COM
        lay.addWidget(self._section_label("Puerto COM"))
        port_row = QHBoxLayout()
        self.combo_port = QComboBox()
        self.combo_port.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.combo_port.setToolTip("Seleccione el puerto COM del ESP32")
        btn_scan = QPushButton("↺")
        btn_scan.setObjectName("btn_scan")
        btn_scan.setFixedSize(28, 28)
        btn_scan.setToolTip("Escanear puertos disponibles")
        btn_scan.clicked.connect(self._scan_ports)
        port_row.addWidget(self.combo_port)
        port_row.addWidget(btn_scan)
        lay.addLayout(port_row)

        # Cámara
        lay.addWidget(self._section_label("Cámara"))
        self.combo_camera = QComboBox()
        for i in range(5):
            self.combo_camera.addItem(f"Cámara {i}  (índice {i})", i)
        self.combo_camera.setCurrentIndex(0)
        lay.addWidget(self.combo_camera)

        # Fase de protocolo
        lay.addWidget(self._section_label("Protocolo Serie"))
        self.combo_phase = QComboBox()
        self.combo_phase.addItem("Fase 1 — Char ASCII  (R/G/Y/N)", 1)
        self.combo_phase.addItem("Fase 2 — Trama RGB  (<A,r,g,b>)", 2)
        lay.addWidget(self.combo_phase)

        lay.addWidget(self._hsep())

        # Botón conectar serial
        self.btn_connect = QPushButton("⚡  Conectar Serial")
        self.btn_connect.setObjectName("btn_connect")
        self.btn_connect.setProperty("connected", "false")
        self.btn_connect.clicked.connect(self._toggle_serial)
        lay.addWidget(self.btn_connect)

        # Botón cámara
        self.btn_camera = QPushButton("▶  Iniciar Cámara")
        self.btn_camera.setObjectName("btn_camera")
        self.btn_camera.setProperty("active", "false")
        self.btn_camera.clicked.connect(self._toggle_camera)
        lay.addWidget(self.btn_camera)

        return gb

    def _build_manual_test_group(self) -> QGroupBox:
        gb = QGroupBox("TEST MANUAL")
        lay = QVBoxLayout(gb)
        lay.setSpacing(6)
        lay.addWidget(self._section_label("Envío de color forzado"))

        grid_widget = QWidget()
        grid = QHBoxLayout(grid_widget)
        grid.setSpacing(6)
        grid.setContentsMargins(0, 0, 0, 0)

        left_col = QVBoxLayout()
        right_col = QVBoxLayout()

        self.btn_rojo = QPushButton("● ROJO")
        self.btn_rojo.setObjectName("btn_rojo")
        self.btn_rojo.clicked.connect(lambda: self._send_manual_color("rojo"))

        self.btn_verde = QPushButton("● VERDE")
        self.btn_verde.setObjectName("btn_verde")
        self.btn_verde.clicked.connect(lambda: self._send_manual_color("verde"))

        self.btn_amarillo = QPushButton("● AMARILLO")
        self.btn_amarillo.setObjectName("btn_amarillo")
        self.btn_amarillo.clicked.connect(lambda: self._send_manual_color("amarillo"))

        self.btn_ninguno = QPushButton("○ APAGAR")
        self.btn_ninguno.setObjectName("btn_ninguno")
        self.btn_ninguno.clicked.connect(lambda: self._send_manual_color("ninguno"))

        left_col.addWidget(self.btn_rojo)
        left_col.addWidget(self.btn_amarillo)
        right_col.addWidget(self.btn_verde)
        right_col.addWidget(self.btn_ninguno)

        grid.addLayout(left_col)
        grid.addLayout(right_col)
        lay.addWidget(grid_widget)
        return gb

    def _build_led_mode_group(self) -> QGroupBox:
        gb = QGroupBox("MODO LED")
        lay = QVBoxLayout(gb)
        lay.setSpacing(6)

        lay.addWidget(self._section_label("Comportamiento de salida"))

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        self.btn_mode_pulso = QPushButton("⚡  PULSO")
        self.btn_mode_pulso.setObjectName("btn_led_mode")
        self.btn_mode_pulso.setProperty("active", "true")
        self.btn_mode_pulso.setToolTip(
            "Envía el comando al detectar un cambio.\n"
            "El LED se apaga por timeout del firmware (~2s)."
        )
        self.btn_mode_pulso.clicked.connect(lambda: self._set_led_mode("pulso"))

        self.btn_mode_continuo = QPushButton("◎  CONTINUO")
        self.btn_mode_continuo.setObjectName("btn_led_mode")
        self.btn_mode_continuo.setProperty("active", "false")
        self.btn_mode_continuo.setToolTip(
            "Envía el comando al detectar Y lo repite cada 1s.\n"
            "El LED sigue la detección en tiempo real."
        )
        self.btn_mode_continuo.clicked.connect(lambda: self._set_led_mode("continuo"))

        btn_row.addWidget(self.btn_mode_pulso)
        btn_row.addWidget(self.btn_mode_continuo)
        lay.addLayout(btn_row)

        self.lbl_led_mode_desc = QLabel(
            "LED activa al detectar;\nse apaga por timeout del firmware."
        )
        self.lbl_led_mode_desc.setObjectName("lbl_section")
        self.lbl_led_mode_desc.setWordWrap(True)
        lay.addWidget(self.lbl_led_mode_desc)

        return gb

    def _set_led_mode(self, mode: str) -> None:
        self._led_mode = mode
        _descs = {
            "pulso":    "LED activa al detectar;\nse apaga por timeout del firmware.",
            "continuo": "LED sigue la detección en tiempo real;\nheartbeat cada 1s mantiene el estado.",
        }
        self.lbl_led_mode_desc.setText(_descs[mode])
        for btn, btn_mode in [
            (self.btn_mode_pulso,    "pulso"),
            (self.btn_mode_continuo, "continuo"),
        ]:
            btn.setProperty("active", "true" if btn_mode == mode else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._log("INFO", f"Modo LED → {mode.upper()}")

    def _build_phase2_group(self) -> QGroupBox:
        gb = QGroupBox("CONTROL RGB  —  FASE 2")
        lay = QVBoxLayout(gb)
        lay.setSpacing(6)
        lay.addWidget(self._section_label("Color global WS2812B"))

        # Preview swatch
        self.lbl_rgb_preview = QLabel()
        self.lbl_rgb_preview.setFixedHeight(28)
        self.lbl_rgb_preview.setStyleSheet(
            f"background-color: #FF0000; border-radius: 4px; border: 1px solid #3A3A3A;"
        )
        lay.addWidget(self.lbl_rgb_preview)

        # Sliders R, G, B
        self._sl_r, self._lv_r = self._make_rgb_slider("R", styles.ERROR)
        self._sl_g, self._lv_g = self._make_rgb_slider("G", styles.SUCCESS)
        self._sl_b, self._lv_b = self._make_rgb_slider("B", styles.ACCENT)

        for label_text, sl, lv, color in [
            ("R", self._sl_r, self._lv_r, styles.ERROR),
            ("G", self._sl_g, self._lv_g, styles.SUCCESS),
            ("B", self._sl_b, self._lv_b, styles.ACCENT),
        ]:
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(12)
            lbl.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 11px;")
            row.addWidget(lbl)
            row.addWidget(sl)
            row.addWidget(lv)
            lay.addLayout(row)

        for sl in (self._sl_r, self._sl_g, self._sl_b):
            sl.valueChanged.connect(self._update_rgb_preview)

        self._sl_r.setValue(255)

        btn_send_rgb = QPushButton("Enviar Color RGB")
        btn_send_rgb.setObjectName("btn_save")
        btn_send_rgb.clicked.connect(self._send_rgb_manual)
        lay.addWidget(btn_send_rgb)

        # Brillo
        lay.addWidget(self._section_label("Brillo global"))
        bright_row = QHBoxLayout()
        self._sl_brightness = QSlider(Qt.Horizontal)
        self._sl_brightness.setRange(0, 255)
        self._sl_brightness.setValue(200)
        self._lv_brightness = QLabel("200")
        self._lv_brightness.setObjectName("lbl_slider_val")
        self._sl_brightness.valueChanged.connect(
            lambda v: self._lv_brightness.setText(str(v))
        )
        bright_row.addWidget(self._sl_brightness)
        bright_row.addWidget(self._lv_brightness)
        lay.addLayout(bright_row)

        btn_brightness = QPushButton("Aplicar Brillo")
        btn_brightness.setObjectName("btn_load")
        btn_brightness.clicked.connect(
            lambda: self._send_and_log(self._serial.send_brightness(self._sl_brightness.value()))
        )
        lay.addWidget(btn_brightness)

        btn_off = QPushButton("⬛  LED Apagar (<OFF>)")
        btn_off.setObjectName("btn_export")
        btn_off.clicked.connect(lambda: self._send_and_log(self._serial.send_off()))
        lay.addWidget(btn_off)

        return gb

    # ── Panel central ──────────────────────────────────────────────────

    def _build_center_panel(self) -> QWidget:
        w = QWidget()
        w.setObjectName("w_center_panel")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(8)

        # Tab de vistas de video
        self.video_tabs = QTabWidget()

        # Vista 1: Video en vivo
        self.lbl_video = QLabel("SIN SEÑAL DE CÁMARA\n\nInicie la cámara con el botón ▶")
        self.lbl_video.setObjectName("lbl_video_placeholder")
        self.lbl_video.setAlignment(Qt.AlignCenter)
        self.lbl_video.setMinimumSize(400, 280)
        self.video_tabs.addTab(self.lbl_video, "VIDEO EN VIVO")

        # Vista 2: Espacio HSV
        self.lbl_hsv = QLabel("SIN SEÑAL DE CÁMARA")
        self.lbl_hsv.setObjectName("lbl_video_placeholder")
        self.lbl_hsv.setAlignment(Qt.AlignCenter)
        self.video_tabs.addTab(self.lbl_hsv, "ESPACIO HSV")

        # Vista 3: Máscaras binarias
        self.lbl_masks = QLabel("SIN SEÑAL DE CÁMARA")
        self.lbl_masks.setObjectName("lbl_video_placeholder")
        self.lbl_masks.setAlignment(Qt.AlignCenter)
        self.video_tabs.addTab(self.lbl_masks, "MÁSCARAS")

        lay.addWidget(self.video_tabs, stretch=1)

        # Barra de color estable
        color_bar = QWidget()
        color_bar.setObjectName("w_color_bar")
        color_bar.setFixedHeight(58)
        bar_lay = QHBoxLayout(color_bar)
        bar_lay.setContentsMargins(16, 4, 16, 4)

        lbl_prefix = QLabel("COLOR ESTABLE:")
        lbl_prefix.setObjectName("lbl_section")
        lbl_prefix.setFixedWidth(110)
        bar_lay.addWidget(lbl_prefix)

        self.lbl_color_big = QLabel("NINGUNO")
        self.lbl_color_big.setObjectName("lbl_color_big")
        self.lbl_color_big.setStyleSheet(f"color: {styles.TEXT_SEC};")
        bar_lay.addWidget(self.lbl_color_big, stretch=1)

        stats_col = QVBoxLayout()
        stats_col.setSpacing(2)
        self.lbl_fps_badge = QLabel("FPS: --.-")
        self.lbl_fps_badge.setObjectName("lbl_fps_badge")
        self.lbl_fps_badge.setAlignment(Qt.AlignRight)
        self.lbl_candidate_badge = QLabel("candidato: —")
        self.lbl_candidate_badge.setObjectName("lbl_section")
        self.lbl_candidate_badge.setAlignment(Qt.AlignRight)
        stats_col.addWidget(self.lbl_fps_badge)
        stats_col.addWidget(self.lbl_candidate_badge)
        bar_lay.addLayout(stats_col)

        lay.addWidget(color_bar)
        return w

    # ── Panel derecho ──────────────────────────────────────────────────

    def _build_right_panel(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFixedWidth(352)

        content = QWidget()
        lay = QVBoxLayout(content)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(10)

        lay.addWidget(self._build_hsv_calibrator())
        lay.addWidget(self._build_filter_group())
        lay.addWidget(self._build_stats_group())
        lay.addWidget(self._build_persistence_buttons())
        lay.addStretch()

        scroll.setWidget(content)
        return scroll

    def _build_hsv_calibrator(self) -> QGroupBox:
        gb = QGroupBox("CALIBRADOR HSV")
        lay = QVBoxLayout(gb)
        lay.setSpacing(6)

        calib_tabs = QTabWidget()

        calib_tabs.addTab(self._build_color_sliders("rojo"),     "ROJO")
        calib_tabs.addTab(self._build_color_sliders("verde"),    "VERDE")
        calib_tabs.addTab(self._build_color_sliders("amarillo"), "AMARILLO")

        lay.addWidget(calib_tabs)
        return gb

    def _build_color_sliders(self, color_key: str) -> QWidget:
        """Crea el panel de 6 sliders para un color. El rojo tiene lógica de doble rango."""
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(6, 8, 6, 6)
        lay.setSpacing(4)

        if color_key == "rojo":
            sliders_def = [
                # (etiqueta, min, max, getter, setter, tooltip)
                ("H bajo max",  0,  30,
                 lambda: int(config.HSV_RANGES["rojo_1"]["upper"][0]),
                 lambda v: self._set_rojo_h_low_max(v),
                 "Límite superior del rojo bajo (H: 0–30)"),
                ("H alto min", 150, 179,
                 lambda: int(config.HSV_RANGES["rojo_2"]["lower"][0]),
                 lambda v: self._set_rojo_h_high_min(v),
                 "Límite inferior del rojo alto (H: 150–179)"),
                ("S  mínimo",   0, 255,
                 lambda: int(config.HSV_RANGES["rojo_1"]["lower"][1]),
                 lambda v: self._set_rojo_s(0, v),
                 "Saturación mínima (compartida por ambos rangos)"),
                ("S  máximo",   0, 255,
                 lambda: int(config.HSV_RANGES["rojo_1"]["upper"][1]),
                 lambda v: self._set_rojo_s(1, v),
                 "Saturación máxima (compartida por ambos rangos)"),
                ("V  mínimo",   0, 255,
                 lambda: int(config.HSV_RANGES["rojo_1"]["lower"][2]),
                 lambda v: self._set_rojo_v(0, v),
                 "Valor mínimo (compartida por ambos rangos)"),
                ("V  máximo",   0, 255,
                 lambda: int(config.HSV_RANGES["rojo_1"]["upper"][2]),
                 lambda v: self._set_rojo_v(1, v),
                 "Valor máximo (compartida por ambos rangos)"),
            ]
        else:
            sliders_def = [
                ("H  mínimo",  0, 179,
                 lambda: int(config.HSV_RANGES[color_key]["lower"][0]),
                 lambda v, k=color_key: self._set_hsv_val(k, "lower", 0, v),
                 "Matiz mínimo (Hue, 0–179)"),
                ("H  máximo",  0, 179,
                 lambda: int(config.HSV_RANGES[color_key]["upper"][0]),
                 lambda v, k=color_key: self._set_hsv_val(k, "upper", 0, v),
                 "Matiz máximo (Hue, 0–179)"),
                ("S  mínimo",  0, 255,
                 lambda: int(config.HSV_RANGES[color_key]["lower"][1]),
                 lambda v, k=color_key: self._set_hsv_val(k, "lower", 1, v),
                 "Saturación mínima (0–255)"),
                ("S  máximo",  0, 255,
                 lambda: int(config.HSV_RANGES[color_key]["upper"][1]),
                 lambda v, k=color_key: self._set_hsv_val(k, "upper", 1, v),
                 "Saturación máxima (0–255)"),
                ("V  mínimo",  0, 255,
                 lambda: int(config.HSV_RANGES[color_key]["lower"][2]),
                 lambda v, k=color_key: self._set_hsv_val(k, "lower", 2, v),
                 "Valor mínimo (0–255)"),
                ("V  máximo",  0, 255,
                 lambda: int(config.HSV_RANGES[color_key]["upper"][2]),
                 lambda v, k=color_key: self._set_hsv_val(k, "upper", 2, v),
                 "Valor máximo (0–255)"),
            ]

        for label_txt, sl_min, sl_max, getter, setter, tip in sliders_def:
            row = QHBoxLayout()
            row.setSpacing(6)
            lbl = QLabel(label_txt)
            lbl.setFixedWidth(72)
            lbl.setObjectName("lbl_section")
            lbl.setToolTip(tip)

            sl = QSlider(Qt.Horizontal)
            sl.setRange(sl_min, sl_max)
            sl.setValue(getter())
            sl.setToolTip(tip)

            val_lbl = QLabel(str(getter()))
            val_lbl.setObjectName("lbl_slider_val")
            val_lbl.setFixedWidth(30)

            def _on_change(v, _setter=setter, _lbl=val_lbl):
                _setter(v)
                _lbl.setText(str(v))

            sl.valueChanged.connect(_on_change)

            row.addWidget(lbl)
            row.addWidget(sl, stretch=1)
            row.addWidget(val_lbl)
            lay.addLayout(row)

        return w

    def _build_filter_group(self) -> QGroupBox:
        gb = QGroupBox("FILTROS ANTI-RUIDO")
        lay = QVBoxLayout(gb)
        lay.setSpacing(6)

        # Píxeles mínimos
        lay.addWidget(self._section_label("Píxeles mínimos activos"))
        px_row = QHBoxLayout()
        self.sl_min_pixels = QSlider(Qt.Horizontal)
        self.sl_min_pixels.setRange(500, 20000)
        self.sl_min_pixels.setValue(config.FILTER_MIN_PIXELS)
        self.sl_min_pixels.setSingleStep(100)
        self.lv_min_pixels = QLabel(str(config.FILTER_MIN_PIXELS))
        self.lv_min_pixels.setObjectName("lbl_slider_val")
        self.lv_min_pixels.setFixedWidth(40)
        self.sl_min_pixels.valueChanged.connect(self._on_filter_change)
        px_row.addWidget(self.sl_min_pixels)
        px_row.addWidget(self.lv_min_pixels)
        lay.addLayout(px_row)

        # Frames de estabilidad
        lay.addWidget(self._section_label("Frames de estabilidad"))
        fr_row = QHBoxLayout()
        self.sl_stability = QSlider(Qt.Horizontal)
        self.sl_stability.setRange(1, 20)
        self.sl_stability.setValue(config.FILTER_STABILITY_FRAMES)
        self.lv_stability = QLabel(str(config.FILTER_STABILITY_FRAMES))
        self.lv_stability.setObjectName("lbl_slider_val")
        self.lv_stability.setFixedWidth(40)
        self.sl_stability.valueChanged.connect(self._on_filter_change)
        fr_row.addWidget(self.sl_stability)
        fr_row.addWidget(self.lv_stability)
        lay.addLayout(fr_row)

        return gb

    def _build_stats_group(self) -> QGroupBox:
        gb = QGroupBox("ESTADÍSTICAS DE SESIÓN")
        lay = QVBoxLayout(gb)
        lay.setSpacing(8)

        counters_row = QHBoxLayout()
        counters_row.setSpacing(6)

        for color_key, hex_color, obj_name in [
            ("rojo",     styles.ERROR,   "rojo"),
            ("verde",    styles.SUCCESS, "verde"),
            ("amarillo", styles.WARNING, "amarillo"),
        ]:
            col = QVBoxLayout()
            col.setSpacing(2)
            cnt_lbl = QLabel("0")
            cnt_lbl.setObjectName("lbl_stat_count")
            cnt_lbl.setStyleSheet(f"color: {hex_color};")
            name_lbl = QLabel(color_key.upper())
            name_lbl.setObjectName("lbl_stat_label")
            col.addWidget(cnt_lbl)
            col.addWidget(name_lbl)
            counters_row.addLayout(col)
            setattr(self, f"lbl_cnt_{color_key}", cnt_lbl)

        lay.addLayout(counters_row)

        # Barras de proporción
        lay.addWidget(self._section_label("Proporción de detecciones"))
        for color_key, obj_name in [("rojo", "pb_rojo"), ("verde", "pb_verde"), ("amarillo", "pb_amarillo")]:
            pb = QProgressBar()
            pb.setObjectName(obj_name)
            pb.setRange(0, 100)
            pb.setValue(0)
            pb.setFixedHeight(8)
            pb.setTextVisible(False)
            lay.addWidget(pb)
            setattr(self, obj_name, pb)

        lay.addWidget(self._hsep())

        # Tiempo de sesión y FPS promedio
        time_row = QHBoxLayout()
        self.lbl_session_time = QLabel("Sesión: 00:00:00")
        self.lbl_session_time.setObjectName("lbl_section")
        self.lbl_avg_fps = QLabel("FPS prom: --.--")
        self.lbl_avg_fps.setObjectName("lbl_section")
        self.lbl_avg_fps.setAlignment(Qt.AlignRight)
        time_row.addWidget(self.lbl_session_time)
        time_row.addWidget(self.lbl_avg_fps)
        lay.addLayout(time_row)

        # Timer para actualizar tiempo de sesión
        self._session_timer = QTimer(self)
        self._session_timer.timeout.connect(self._update_session_time)
        self._session_timer.start(1000)

        return gb

    def _build_persistence_buttons(self) -> QGroupBox:
        gb = QGroupBox("PERFIL DE CALIBRACIÓN")
        lay = QVBoxLayout(gb)
        lay.setSpacing(6)

        btn_row1 = QHBoxLayout()
        btn_save = QPushButton("💾  Guardar Perfil")
        btn_save.setObjectName("btn_save")
        btn_save.clicked.connect(self._save_config)
        btn_load = QPushButton("📂  Cargar Perfil")
        btn_load.setObjectName("btn_load")
        btn_load.clicked.connect(self._load_config)
        btn_row1.addWidget(btn_save)
        btn_row1.addWidget(btn_load)
        lay.addLayout(btn_row1)

        btn_export = QPushButton("📄  Exportar Reporte (.txt)")
        btn_export.setObjectName("btn_export")
        btn_export.clicked.connect(self._export_report)
        lay.addWidget(btn_export)

        return gb

    # ── Log terminal ───────────────────────────────────────────────────

    def _build_log_panel(self) -> QWidget:
        w = QWidget()
        w.setFixedHeight(108)
        lay = QHBoxLayout(w)
        lay.setContentsMargins(8, 4, 8, 6)
        lay.setSpacing(6)

        icon_lbl = QLabel("TERMINAL")
        icon_lbl.setObjectName("lbl_section")
        icon_lbl.setFixedWidth(60)
        icon_lbl.setAlignment(Qt.AlignTop)

        self.log_terminal = QPlainTextEdit()
        self.log_terminal.setObjectName("log_terminal")
        self.log_terminal.setReadOnly(True)
        self.log_terminal.setMaximumBlockCount(200)

        lay.addWidget(icon_lbl)
        lay.addWidget(self.log_terminal)
        return w

    # ------------------------------------------------------------------ #
    # Conexión de señales
    # ------------------------------------------------------------------ #

    def _connect_signals(self) -> None:
        self._camera.frame_ready.connect(self._on_frame_ready)
        self._camera.hsv_ready.connect(self._on_hsv_ready)
        self._camera.masks_ready.connect(self._on_masks_ready)
        self._camera.stats_updated.connect(self._on_stats_updated)
        self._camera.color_confirmed.connect(self._on_color_confirmed)
        self._camera.error_occurred.connect(self._on_camera_error)

    # ------------------------------------------------------------------ #
    # Slots de cámara
    # ------------------------------------------------------------------ #

    def _on_frame_ready(self, qimage) -> None:
        px = QPixmap.fromImage(qimage)
        scaled = px.scaled(self.lbl_video.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.lbl_video.setPixmap(scaled)

    def _on_hsv_ready(self, qimage) -> None:
        px = QPixmap.fromImage(qimage)
        scaled = px.scaled(self.lbl_hsv.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.lbl_hsv.setPixmap(scaled)

    def _on_masks_ready(self, qimage) -> None:
        px = QPixmap.fromImage(qimage)
        scaled = px.scaled(self.lbl_masks.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.lbl_masks.setPixmap(scaled)

    def _on_stats_updated(self, stats: dict) -> None:
        fps = stats.get("fps", 0.0)
        self._last_fps = fps
        confirmed = stats.get("confirmed", "ninguno")
        candidate = stats.get("candidate", "ninguno")

        # Mantener el último color confirmado para el heartbeat en modo continuo
        self._current_confirmed = confirmed

        self.lbl_fps_badge.setText(f"FPS: {fps:5.1f}")
        self.lbl_candidate_badge.setText(f"candidato: {candidate.upper()}")

        meta = config.COLOR_METADATA.get(confirmed, config.COLOR_METADATA["ninguno"])
        self.lbl_color_big.setText(meta["label"])
        self.lbl_color_big.setStyleSheet(f"color: {meta['hex']}; font-size:20px; font-weight:bold; letter-spacing:4px;")

    def _on_color_confirmed(self, color: str) -> None:
        # Actualizar contadores de estadísticas
        if color in self._detection_counts:
            self._detection_counts[color] += 1
            self._refresh_stats_bars()

        # Envío automático si Link Mode activo
        if self._link_active and self._serial.is_connected:
            log_msg = self._serial.send_color(color)
            meta = config.COLOR_METADATA.get(color, config.COLOR_METADATA["ninguno"])
            mode_prefix = "MOCK" if self._serial.is_mock else self._serial.port
            self._log("TX", f"[{mode_prefix}] {log_msg}")

    def _on_camera_error(self, msg: str) -> None:
        self._log("ERROR", f"Cámara: {msg}")
        self._camera_active = False
        self._update_camera_btn_state()

    # ------------------------------------------------------------------ #
    # Acciones de la UI
    # ------------------------------------------------------------------ #

    def _toggle_serial(self) -> None:
        if self._serial_connected:
            msg = self._serial.disconnect()
            self._serial_connected = False
            self._log("INFO", msg)
            self._update_serial_state(connected=False, mock=False)
            if self._link_active:
                self._toggle_link()
            self._heartbeat_timer.stop()
        else:
            port = self.combo_port.currentText()
            phase = self.combo_phase.currentData()
            if not port:
                self._log("ERROR", "Seleccione un puerto COM antes de conectar.")
                return
            self.btn_connect.setEnabled(False)
            self._log("INFO", f"Conectando a {port} (Fase {phase})... aguarde ~1.5s")
            self._serial.connect_async(port, config.SERIAL_BAUDRATE, phase, self._on_serial_connect_done)

    def _on_serial_connect_done(self, success: bool, msg: str) -> None:
        self.btn_connect.setEnabled(True)
        if success:
            self._serial_connected = True
            self._log("OK" if not self._serial.is_mock else "MOCK", msg)
            self._update_serial_state(connected=True, mock=self._serial.is_mock)
            self._heartbeat_timer.start(1000)
        else:
            self._log("ERROR", msg)
            self._update_serial_state(connected=False, mock=True)
            # Se activa mock automáticamente
            self._serial_connected = True
            self._heartbeat_timer.start(1000)

    def _update_serial_state(self, connected: bool, mock: bool) -> None:
        if connected and not mock:
            self.led_status.set_state("connected")
            self.lbl_status_text.setText(f"CONECTADO  {self._serial.port}")
            self.btn_connect.setText("✖  Desconectar Serial")
            self.btn_connect.setProperty("connected", "true")
        elif connected and mock:
            self.led_status.set_state("mock")
            self.lbl_status_text.setText("SIMULACIÓN  (mock)")
            self.btn_connect.setText("✖  Desconectar")
            self.btn_connect.setProperty("connected", "true")
        else:
            self.led_status.set_state("off")
            self.lbl_status_text.setText("SIN CONEXIÓN")
            self.btn_connect.setText("⚡  Conectar Serial")
            self.btn_connect.setProperty("connected", "false")
        # Forzar recarga del QSS (las propiedades dinámicas requieren esto)
        self.btn_connect.style().unpolish(self.btn_connect)
        self.btn_connect.style().polish(self.btn_connect)

    def _toggle_camera(self) -> None:
        if self._camera_active:
            self._camera.stop_capture()
            self._camera_active = False
            self.lbl_video.setPixmap(QPixmap())
            self.lbl_video.setText("SIN SEÑAL DE CÁMARA\n\nInicie la cámara con el botón ▶")
            self.lbl_hsv.setPixmap(QPixmap())
            self.lbl_hsv.setText("SIN SEÑAL DE CÁMARA")
            self.lbl_masks.setPixmap(QPixmap())
            self.lbl_masks.setText("SIN SEÑAL DE CÁMARA")
            self._log("INFO", "Cámara detenida.")
        else:
            cam_idx = self.combo_camera.currentData()
            self._log("INFO", f"Iniciando cámara {cam_idx}...")
            self._camera.start_capture(cam_idx)
            self._camera_active = True
            self._log("OK", f"Captura iniciada (cámara {cam_idx}).")
        self._update_camera_btn_state()

    def _update_camera_btn_state(self) -> None:
        if self._camera_active:
            self.btn_camera.setText("■  Detener Cámara")
            self.btn_camera.setProperty("active", "true")
        else:
            self.btn_camera.setText("▶  Iniciar Cámara")
            self.btn_camera.setProperty("active", "false")
        self.btn_camera.style().unpolish(self.btn_camera)
        self.btn_camera.style().polish(self.btn_camera)

    def _toggle_link(self) -> None:
        self._link_active = not self._link_active
        if self._link_active:
            self.btn_link.setText("■  LINK MODE  ACTIVO")
            self.btn_link.setProperty("active", "true")
            self._link_btn_effect.setBlurRadius(18)
            self.led_status.set_state("link")
            self._log("OK", "▶ LINK MODE activado — detección automática iniciada.")
        else:
            self.btn_link.setText("▶  LINK MODE")
            self.btn_link.setProperty("active", "false")
            self._link_btn_effect.setBlurRadius(0)
            state = "connected" if (self._serial_connected and not self._serial.is_mock) else \
                    "mock" if self._serial_connected else "off"
            self.led_status.set_state(state)
            self._log("INFO", "■ LINK MODE desactivado — control manual.")
        self.btn_link.style().unpolish(self.btn_link)
        self.btn_link.style().polish(self.btn_link)

    def _send_manual_color(self, color: str) -> None:
        if not self._serial.is_connected:
            self._log("ERROR", "Sin conexión serial. Conecte primero.")
            return
        log_msg = self._serial.send_color(color)
        mode = "MOCK" if self._serial.is_mock else self._serial.port
        self._log("TX", f"[{mode}] Manual → {log_msg}")

    def _send_rgb_manual(self) -> None:
        r = self._sl_r.value()
        g = self._sl_g.value()
        b = self._sl_b.value()
        log_msg = self._serial.send_rgb(r, g, b)
        mode = "MOCK" if self._serial.is_mock else self._serial.port
        self._log("TX", f"[{mode}] {log_msg}")

    def _send_and_log(self, log_msg: str) -> None:
        if not self._serial.is_connected:
            self._log("ERROR", "Sin conexión serial.")
            return
        mode = "MOCK" if self._serial.is_mock else self._serial.port
        self._log("TX", f"[{mode}] {log_msg}")

    def _scan_ports(self) -> None:
        ports = SerialCommunicator.get_available_ports()
        self.combo_port.clear()
        if ports:
            self.combo_port.addItems(ports)
            self._log("INFO", f"Puertos detectados: {', '.join(ports)}")
        else:
            self.combo_port.addItem("(sin puertos COM)")
            self._log("WARN", "No se detectaron puertos COM. Modo simulación disponible.")

    # ------------------------------------------------------------------ #
    # HSV Calibrator setters
    # ------------------------------------------------------------------ #

    def _set_hsv_val(self, color_key: str, bound: str, channel: int, value: int) -> None:
        config.HSV_RANGES[color_key][bound][channel] = value

    def _set_rojo_h_low_max(self, v: int) -> None:
        config.HSV_RANGES["rojo_1"]["upper"][0] = v

    def _set_rojo_h_high_min(self, v: int) -> None:
        config.HSV_RANGES["rojo_2"]["lower"][0] = v

    def _set_rojo_s(self, bound_idx: int, v: int) -> None:
        bounds = ("lower", "upper")
        config.HSV_RANGES["rojo_1"][bounds[bound_idx]][1] = v
        config.HSV_RANGES["rojo_2"][bounds[bound_idx]][1] = v

    def _set_rojo_v(self, bound_idx: int, v: int) -> None:
        bounds = ("lower", "upper")
        config.HSV_RANGES["rojo_1"][bounds[bound_idx]][2] = v
        config.HSV_RANGES["rojo_2"][bounds[bound_idx]][2] = v

    # ------------------------------------------------------------------ #
    # Filtros
    # ------------------------------------------------------------------ #

    def _on_filter_change(self) -> None:
        mp = self.sl_min_pixels.value()
        sf = self.sl_stability.value()
        self.lv_min_pixels.setText(str(mp))
        self.lv_stability.setText(str(sf))
        self._camera.update_filter_thresholds(mp, sf)

    # ------------------------------------------------------------------ #
    # Estadísticas
    # ------------------------------------------------------------------ #

    def _refresh_stats_bars(self) -> None:
        total = sum(self._detection_counts.values()) or 1
        for color in ("rojo", "verde", "amarillo"):
            count = self._detection_counts[color]
            pct = int(count * 100 / total)
            getattr(self, f"pb_{color}").setValue(pct)
            getattr(self, f"lbl_cnt_{color}").setText(str(count))

    def _update_session_time(self) -> None:
        elapsed = int(time.time() - self._session_start)
        h, rem = divmod(elapsed, 3600)
        m, s = divmod(rem, 60)
        self.lbl_session_time.setText(f"Sesión: {h:02d}:{m:02d}:{s:02d}")
        self.lbl_avg_fps.setText(f"FPS: {self._last_fps:.1f}")

    # ------------------------------------------------------------------ #
    # Persistencia
    # ------------------------------------------------------------------ #

    def _save_config(self) -> None:
        msg = config.save_config(
            self.sl_min_pixels.value(),
            self.sl_stability.value(),
        )
        self._log("OK", msg)

    def _load_config(self) -> None:
        success, msg = config.load_config()
        self._log("OK" if success else "WARN", msg)
        if success:
            self._refresh_sliders_from_config()

    def _refresh_sliders_from_config(self) -> None:
        self.sl_min_pixels.setValue(config.FILTER_MIN_PIXELS)
        self.sl_stability.setValue(config.FILTER_STABILITY_FRAMES)
        # Los sliders HSV se actualizan solos la próxima vez que se abre el calibrador.
        # Para un refresco inmediato se necesitaría guardar referencias a cada slider.
        # Esta deuda está registrada (ver deudaTecnica.md).

    def _export_report(self) -> None:
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            f"reporte_tp2_{ts}.txt"
        )
        elapsed = int(time.time() - self._session_start)
        total_det = sum(self._detection_counts.values()) or 1

        lines = [
            "=" * 60,
            "  REPORTE TP2 — VISIÓN ARTIFICIAL Y CONTROL DE COLOR",
            "  UTN FRC | Alumno: Cristian Gonzalo Vera | Legajo: 420581",
            "=" * 60,
            f"  Fecha/Hora : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"  Puerto     : {self._serial.port or 'N/A'}",
            f"  Protocolo  : Fase {self._serial.phase}",
            f"  Sesión     : {elapsed // 3600:02d}h {(elapsed % 3600) // 60:02d}m {elapsed % 60:02d}s",
            f"  FPS aprox. : {self._last_fps:.1f}",
            "",
            "── DETECCIONES ────────────────────────────────────────────",
        ]
        for color in ("rojo", "verde", "amarillo"):
            count = self._detection_counts[color]
            pct = count * 100 / total_det
            lines.append(f"  {color.upper():10s}: {count:6d}  ({pct:5.1f}%)")
        lines += [
            "",
            "── CALIBRACIÓN HSV ACTUAL ─────────────────────────────────",
        ]
        for key, rng in config.HSV_RANGES.items():
            lo = rng["lower"].tolist()
            hi = rng["upper"].tolist()
            lines.append(f"  {key:12s}: lower={lo}  upper={hi}")
        lines += [
            "",
            "── FILTROS ────────────────────────────────────────────────",
            f"  Píxeles mínimos : {self.sl_min_pixels.value()}",
            f"  Frames estables : {self.sl_stability.value()}",
            "",
            "=" * 60,
        ]

        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            self._log("OK", f"Reporte exportado: {os.path.basename(report_path)}")
        except OSError as e:
            self._log("ERROR", f"No se pudo exportar el reporte: {e}")

    # ------------------------------------------------------------------ #
    # Timers
    # ------------------------------------------------------------------ #

    def _on_heartbeat(self) -> None:
        if not self._link_active or not self._serial.is_connected:
            return
        # Modo CONTINUO: reenvía el color actual cada tick para mantener el LED activo.
        # Modo PULSO: el envío diferencial de _on_color_confirmed es suficiente.
        if self._led_mode == "continuo":
            log_msg = self._serial.send_color(self._current_confirmed)
            mode_prefix = "MOCK" if self._serial.is_mock else self._serial.port
            self._log("TX", f"[{mode_prefix}] ♻ {log_msg}")

    def _on_blink_tick(self) -> None:
        self._blink_state = not self._blink_state

    # ------------------------------------------------------------------ #
    # Log terminal
    # ------------------------------------------------------------------ #

    _LOG_COLORS = {
        "INFO":  "#8899AA",
        "OK":    "#00E676",
        "TX":    "#00D4FF",
        "WARN":  "#FFD600",
        "ERROR": "#FF4444",
        "MOCK":  "#AA8800",
    }

    def _log(self, level: str, msg: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        color = self._LOG_COLORS.get(level, "#8899AA")
        html = (
            f'<span style="color:#4A5A6A;">[{ts}]</span> '
            f'<span style="color:{color}; font-weight:bold;">[{level}]</span> '
            f'<span style="color:#C0C8D8;">{msg}</span>'
        )
        self.log_terminal.appendHtml(html)
        sb = self.log_terminal.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ------------------------------------------------------------------ #
    # RGB preview helper
    # ------------------------------------------------------------------ #

    def _update_rgb_preview(self) -> None:
        r = self._sl_r.value()
        g = self._sl_g.value()
        b = self._sl_b.value()
        self._lv_r.setText(str(r))
        self._lv_g.setText(str(g))
        self._lv_b.setText(str(b))
        self.lbl_rgb_preview.setStyleSheet(
            f"background-color: rgb({r},{g},{b}); border-radius: 4px; border: 1px solid #3A3A3A;"
        )

    def _make_rgb_slider(self, label: str, color: str):
        sl = QSlider(Qt.Horizontal)
        sl.setRange(0, 255)
        sl.setValue(0)
        lv = QLabel("0")
        lv.setObjectName("lbl_slider_val")
        lv.setFixedWidth(30)
        return sl, lv

    # ------------------------------------------------------------------ #
    # Utilidades de layout
    # ------------------------------------------------------------------ #

    @staticmethod
    def _section_label(text: str) -> QLabel:
        lbl = QLabel(text.upper())
        lbl.setObjectName("lbl_section")
        return lbl

    @staticmethod
    def _hsep() -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        return sep

    # ------------------------------------------------------------------ #
    # Cierre limpio
    # ------------------------------------------------------------------ #

    def closeEvent(self, event) -> None:
        self._link_active = False
        self._heartbeat_timer.stop()
        self._session_timer.stop()
        if self._camera_active:
            self._camera.stop_capture()
        if self._serial.is_connected:
            self._serial.disconnect()
        event.accept()
