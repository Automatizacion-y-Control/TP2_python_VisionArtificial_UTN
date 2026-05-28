from collections import deque
import config


class AntiNoiseFilter:
    """
    Filtrado en cascada: espacial → temporal → diferencial.
    Los umbrales son ajustables en caliente desde la UI de calibración.
    """

    def __init__(self):
        self.min_pixels: int = config.FILTER_MIN_PIXELS
        self._stability_limit: int = config.FILTER_STABILITY_FRAMES
        self._history: deque = deque(maxlen=self._stability_limit)
        self._last_sent: str = "ninguno"
        self._fill_history()

    # ------------------------------------------------------------------ #

    def update_thresholds(self, min_pixels: int, stability_frames: int) -> None:
        self.min_pixels = max(1, min_pixels)
        if stability_frames != self._stability_limit:
            self._stability_limit = max(1, stability_frames)
            self._history = deque(maxlen=self._stability_limit)
            self._fill_history()

    # ------------------------------------------------------------------ #

    def filter_detection(self, pixel_counts: dict) -> tuple:
        """
        Retorna (confirmed_color, should_send, active_candidate).
        - confirmed_color: color estable actual.
        - should_send: True si el color cambió (enviar por serial).
        - active_candidate: color candidato del frame actual (pre-estabilización).
        """
        # Filtro 1 — umbral espacial: descarta candidatos con pocos píxeles
        active_candidate = "ninguno"
        max_px = 0
        for color, count in pixel_counts.items():
            if count >= self.min_pixels and count > max_px:
                max_px = count
                active_candidate = color

        # Filtro 2 — estabilidad temporal: todos los frames del historial iguales
        self._history.append(active_candidate)
        first = self._history[0]
        is_stable = all(c == first for c in self._history)
        confirmed_color = first if is_stable else self._last_sent

        # Filtro 3 — diferencial: sólo emitir si hubo cambio real
        should_send = confirmed_color != self._last_sent
        if should_send:
            self._last_sent = confirmed_color

        return confirmed_color, should_send, active_candidate

    def reset(self) -> None:
        self._last_sent = "ninguno"
        self._fill_history()

    def _fill_history(self) -> None:
        self._history.clear()
        for _ in range(self._stability_limit):
            self._history.append("ninguno")
