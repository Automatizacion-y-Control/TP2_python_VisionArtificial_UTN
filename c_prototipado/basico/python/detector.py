# detector.py
"""
Módulo encargado del procesamiento digital de imágenes y segmentación cromática.
Implementa la clase ColorDetector utilizando OpenCV.
"""

import cv2
import numpy as np
from config import HSV_RANGES, APPLY_MORPHOLOGY, MORPHOLOGY_KERNEL_SIZE, APPLY_GAUSSIAN_BLUR, GAUSSIAN_BLUR_KERNEL

class ColorDetector:
    def __init__(self):
        # Crear kernel para operaciones morfológicas
        self.kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, 
            (MORPHOLOGY_KERNEL_SIZE, MORPHOLOGY_KERNEL_SIZE)
        )

    def process_frame(self, frame):
        """
        Recibe un frame en BGR, lo preprocesa, convierte a HSV, genera las máscaras
        de color, aplica morfología y retorna las máscaras junto con el conteo de píxeles.
        """
        # 1. Preprocesamiento: Suavizado Gaussiano para reducir ruido de alta frecuencia
        if APPLY_GAUSSIAN_BLUR:
            processed = cv2.GaussianBlur(frame, GAUSSIAN_BLUR_KERNEL, 0)
        else:
            processed = frame.copy()

        # 2. Conversión de espacio de color BGR -> HSV
        hsv = cv2.cvtColor(processed, cv2.COLOR_BGR2HSV)

        # 3. Segmentación cromática por color
        masks = {}

        # 3.1. Verde
        masks["verde"] = cv2.inRange(
            hsv, 
            HSV_RANGES["verde"]["lower"], 
            HSV_RANGES["verde"]["upper"]
        )

        # 3.2. Amarillo
        masks["amarillo"] = cv2.inRange(
            hsv, 
            HSV_RANGES["amarillo"]["lower"], 
            HSV_RANGES["amarillo"]["upper"]
        )

        # 3.3. Rojo (Unión de ambos extremos del espectro circular de Hue)
        mask_red_1 = cv2.inRange(
            hsv, 
            HSV_RANGES["rojo_1"]["lower"], 
            HSV_RANGES["rojo_1"]["upper"]
        )
        mask_red_2 = cv2.inRange(
            hsv, 
            HSV_RANGES["rojo_2"]["lower"], 
            HSV_RANGES["rojo_2"]["upper"]
        )
        # Suma saturada de OpenCV para unir ambas máscaras
        masks["rojo"] = cv2.add(mask_red_1, mask_red_2)

        # 4. Postprocesamiento: Cierre morfológico para rellenar huecos y suavizar contornos
        if APPLY_MORPHOLOGY:
            for color in ["verde", "amarillo", "rojo"]:
                masks[color] = cv2.morphologyEx(masks[color], cv2.MORPH_CLOSE, self.kernel)

        # 5. Cuantificación de color: Conteo de píxeles activos (no nulos) en cada máscara
        pixel_counts = {
            "verde": cv2.countNonZero(masks["verde"]),
            "amarillo": cv2.countNonZero(masks["amarillo"]),
            "rojo": cv2.countNonZero(masks["rojo"])
        }

        return hsv, masks, pixel_counts
