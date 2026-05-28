# filters.py
"""
Módulo para el filtrado anti-ruido espacial y temporal de las detecciones.
Implementa la lógica en cascada para evitar parpadeos y saturación en el puerto serie.
"""

from collections import deque
from config import FILTER_MIN_PIXELS, FILTER_STABILITY_FRAMES

class AntiNoiseFilter:
    def __init__(self):
        # Umbral mínimo de píxeles activos para evitar falsos positivos
        self.min_pixels = FILTER_MIN_PIXELS
        
        # Historial de frames consecutivos para estabilidad temporal
        self.stability_limit = FILTER_STABILITY_FRAMES
        self.history = deque(maxlen=self.stability_limit)
        
        # Último color que fue confirmado y transmitido por el puerto serie
        self.last_sent_color = "ninguno"
        
        # Inicializar el historial lleno con "ninguno" para estabilidad de arranque
        for _ in range(self.stability_limit):
            self.history.append("ninguno")

    def filter_detection(self, pixel_counts):
        """
        Aplica los filtros en cadena sobre el conteo de píxeles de cada color.
        Retorna:
            - confirmed_color (str): El color actualmente confirmado (estable).
            - should_send (bool): True si el color confirmado cambió y debe enviarse.
            - active_candidate (str): El color candidato para el frame actual.
        """
        # FILTRO 1: Descarte de ruido por umbral de píxeles mínimos y búsqueda de color predominante
        active_candidate = "ninguno"
        max_pixels = 0

        for color, count in pixel_counts.items():
            # Solo consideramos el color si supera el umbral mínimo
            if count >= self.min_pixels:
                if count > max_pixels:
                    max_pixels = count
                    active_candidate = color

        # FILTRO 2: Estabilidad temporal (Historial de frames)
        self.history.append(active_candidate)
        
        # Verificar si todos los elementos en el historial son idénticos
        first_in_history = self.history[0]
        is_stable = all(color == first_in_history for color in self.history)
        
        confirmed_color = first_in_history if is_stable else self.last_sent_color

        # FILTRO 3: Envío diferencial (evitar saturación de comandos redundantes)
        should_send = False
        if confirmed_color != self.last_sent_color:
            self.last_sent_color = confirmed_color
            should_send = True

        return confirmed_color, should_send, active_candidate
