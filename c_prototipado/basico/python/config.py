# config.py
"""
Configuración general de parámetros para el Trabajo Práctico Nº2.
Define los rangos HSV de calibración, parámetros de comunicación serial
y umbrales para los filtros de estabilidad temporal.
"""

import numpy as np

# ==============================================================================
# 1. RANGOS HSV DE CALIBRACIÓN DE COLORES (OpenCV 8-bits: H [0-179], S [0-255], V [0-255])
# ==============================================================================
HSV_RANGES = {
    "verde": {
        "lower": np.array([35, 70, 40], dtype=np.uint8),
        "upper": np.array([85, 255, 255], dtype=np.uint8)
    },
    "amarillo": {
        "lower": np.array([20, 95, 95], dtype=np.uint8),
        "upper": np.array([38, 255, 255], dtype=np.uint8)
    },
    # El color rojo se desdobla en dos rangos por la naturaleza circular de H
    "rojo_1": {
        "lower": np.array([0, 125, 60], dtype=np.uint8),
        "upper": np.array([10, 255, 255], dtype=np.uint8)
    },
    "rojo_2": {
        "lower": np.array([170, 125, 60], dtype=np.uint8),
        "upper": np.array([179, 255, 255], dtype=np.uint8)
    }
}

# Mapeo de nombres internos a etiquetas legibles y colores RGB de visualización (BGR para OpenCV)
COLOR_METADATA = {
    "verde": {"label": "VERDE", "color_bgr": (0, 255, 0), "cmd": "G", "rgb": (0, 255, 0)},
    "amarillo": {"label": "AMARILLO", "color_bgr": (0, 255, 255), "cmd": "Y", "rgb": (255, 200, 0)},
    "rojo": {"label": "ROJO", "color_bgr": (0, 0, 255), "cmd": "R", "rgb": (255, 0, 0)},
    "ninguno": {"label": "NINGUNO", "color_bgr": (128, 128, 128), "cmd": "N", "rgb": (0, 0, 0)}
}

# ==============================================================================
# 2. PARÁMETROS DEL FILTRO ANTI-RUIDO Y DECISIÓN
# ==============================================================================
# Cantidad mínima de píxeles activos en la máscara para considerar válida la detección (evita ruido de fondo)
FILTER_MIN_PIXELS = 4000

# Cantidad de frames consecutivos donde el color debe mantenerse para confirmarse
FILTER_STABILITY_FRAMES = 5

# Aplicar operaciones morfológicas de cierre para limpiar ruido en las máscaras
APPLY_MORPHOLOGY = True
MORPHOLOGY_KERNEL_SIZE = 5

# Suavizado Gaussiano previo para eliminar ruido de alta frecuencia de la cámara
APPLY_GAUSSIAN_BLUR = True
GAUSSIAN_BLUR_KERNEL = (5, 5)

# ==============================================================================
# 3. PARÁMETROS DE COMUNICACIÓN SERIAL
# ==============================================================================
# Puerto serial por defecto (se buscará automáticamente si este no está disponible)
SERIAL_PORT = "COM11"
SERIAL_BAUDRATE = 115200

# Fase de protocolo activa:
# 1 = Carácter Único ('R', 'G', 'Y', 'N')
# 2 = Trama Dinámica RGB ('<R,G,B>\n')
SERIAL_PROTOCOL_PHASE = 1

# ==============================================================================
# 4. CAPTURA Y CONFIGURACIÓN DE VIDEO
# ==============================================================================
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
DISPLAY_WINDOWS = True
