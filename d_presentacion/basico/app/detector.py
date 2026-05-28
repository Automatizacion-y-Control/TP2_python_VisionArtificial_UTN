import cv2
import numpy as np
import config


class ColorDetector:
    """
    Segmentación cromática en espacio HSV.
    Lee config.HSV_RANGES en cada llamada, permitiendo calibración en vivo desde la UI.
    """

    def __init__(self):
        self._kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (config.MORPHOLOGY_KERNEL_SIZE, config.MORPHOLOGY_KERNEL_SIZE),
        )

    def process_frame(self, frame: np.ndarray) -> tuple:
        """
        Recibe frame BGR → retorna (hsv, masks_dict, pixel_counts_dict).
        masks_dict keys: 'rojo', 'verde', 'amarillo'.
        """
        if config.APPLY_GAUSSIAN_BLUR:
            processed = cv2.GaussianBlur(frame, config.GAUSSIAN_BLUR_KERNEL, 0)
        else:
            processed = frame

        hsv = cv2.cvtColor(processed, cv2.COLOR_BGR2HSV)

        # Máscaras individuales
        mask_verde = cv2.inRange(
            hsv,
            config.HSV_RANGES["verde"]["lower"],
            config.HSV_RANGES["verde"]["upper"],
        )
        mask_amarillo = cv2.inRange(
            hsv,
            config.HSV_RANGES["amarillo"]["lower"],
            config.HSV_RANGES["amarillo"]["upper"],
        )

        # Rojo: suma saturada de dos rangos (extremos del canal H circular)
        mask_r1 = cv2.inRange(
            hsv,
            config.HSV_RANGES["rojo_1"]["lower"],
            config.HSV_RANGES["rojo_1"]["upper"],
        )
        mask_r2 = cv2.inRange(
            hsv,
            config.HSV_RANGES["rojo_2"]["lower"],
            config.HSV_RANGES["rojo_2"]["upper"],
        )
        mask_rojo = cv2.add(mask_r1, mask_r2)

        masks = {
            "verde": mask_verde,
            "amarillo": mask_amarillo,
            "rojo": mask_rojo,
        }

        if config.APPLY_MORPHOLOGY:
            for key in masks:
                masks[key] = cv2.morphologyEx(masks[key], cv2.MORPH_CLOSE, self._kernel)

        pixel_counts = {c: cv2.countNonZero(masks[c]) for c in masks}

        return hsv, masks, pixel_counts
