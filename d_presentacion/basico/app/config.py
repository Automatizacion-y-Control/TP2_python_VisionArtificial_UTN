import json
import os
import numpy as np

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calibration.json")

# Rangos HSV calibrados para Redragon HD (H:0-179, S:0-255, V:0-255)
HSV_RANGES = {
    "verde": {
        "lower": np.array([35, 70, 40], dtype=np.uint8),
        "upper": np.array([85, 255, 255], dtype=np.uint8),
    },
    "amarillo": {
        "lower": np.array([20, 95, 95], dtype=np.uint8),
        "upper": np.array([38, 255, 255], dtype=np.uint8),
    },
    # Rojo se divide en dos rangos por la naturaleza circular del canal H
    "rojo_1": {
        "lower": np.array([0, 125, 60], dtype=np.uint8),
        "upper": np.array([10, 255, 255], dtype=np.uint8),
    },
    "rojo_2": {
        "lower": np.array([170, 125, 60], dtype=np.uint8),
        "upper": np.array([179, 255, 255], dtype=np.uint8),
    },
}

COLOR_METADATA = {
    "verde": {
        "label": "VERDE",
        "color_bgr": (0, 200, 50),
        "cmd": "G",
        "rgb": (0, 255, 0),
        "hex": "#00E676",
        "dark_hex": "#0A2A15",
    },
    "amarillo": {
        "label": "AMARILLO",
        "color_bgr": (0, 200, 200),
        "cmd": "Y",
        "rgb": (255, 200, 0),
        "hex": "#FFD600",
        "dark_hex": "#2A2000",
    },
    "rojo": {
        "label": "ROJO",
        "color_bgr": (50, 50, 200),
        "cmd": "R",
        "rgb": (255, 0, 0),
        "hex": "#FF4444",
        "dark_hex": "#2A0A0A",
    },
    "ninguno": {
        "label": "NINGUNO",
        "color_bgr": (80, 80, 80),
        "cmd": "N",
        "rgb": (0, 0, 0),
        "hex": "#445566",
        "dark_hex": "#0C1017",
    },
}

# Parámetros de filtrado
FILTER_MIN_PIXELS = 4000
FILTER_STABILITY_FRAMES = 5
APPLY_MORPHOLOGY = True
MORPHOLOGY_KERNEL_SIZE = 5
APPLY_GAUSSIAN_BLUR = True
GAUSSIAN_BLUR_KERNEL = (5, 5)

# Comunicación serial
SERIAL_BAUDRATE = 115200

# Captura de video
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480


def save_config(filter_min_pixels: int, filter_stability_frames: int) -> str:
    data = {
        "hsv_ranges": {
            k: {
                "lower": v["lower"].tolist(),
                "upper": v["upper"].tolist(),
            }
            for k, v in HSV_RANGES.items()
        },
        "filter_min_pixels": filter_min_pixels,
        "filter_stability_frames": filter_stability_frames,
    }
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return f"Perfil guardado en {os.path.basename(CONFIG_FILE)}."
    except OSError as e:
        return f"Error al guardar: {e}"


def load_config() -> tuple[bool, str]:
    global FILTER_MIN_PIXELS, FILTER_STABILITY_FRAMES
    if not os.path.exists(CONFIG_FILE):
        return False, "Archivo calibration.json no encontrado — usando valores por defecto."
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            data = json.load(f)

        for key, val in data.get("hsv_ranges", {}).items():
            lo = list(val["lower"])
            hi = list(val["upper"])
            if len(lo) != 3 or len(hi) != 3:
                raise ValueError(f"Rango inválido en '{key}'.")
            if not all(0 <= x <= 255 for x in lo + hi):
                raise ValueError(f"Valores fuera de [0-255] en '{key}'.")
            # Validar H dentro de rango OpenCV
            if key in ("verde", "amarillo"):
                if not (0 <= lo[0] <= 179 and 0 <= hi[0] <= 179):
                    raise ValueError(f"Canal H fuera de [0-179] en '{key}'.")
            HSV_RANGES[key]["lower"][:] = np.array(lo, dtype=np.uint8)
            HSV_RANGES[key]["upper"][:] = np.array(hi, dtype=np.uint8)

        mp = int(data.get("filter_min_pixels", FILTER_MIN_PIXELS))
        sf = int(data.get("filter_stability_frames", FILTER_STABILITY_FRAMES))
        if not (100 <= mp <= 100_000):
            raise ValueError("filter_min_pixels fuera de rango.")
        if not (1 <= sf <= 30):
            raise ValueError("filter_stability_frames fuera de rango.")
        FILTER_MIN_PIXELS = mp
        FILTER_STABILITY_FRAMES = sf

        return True, "Calibración cargada correctamente desde calibration.json."
    except Exception as e:
        return False, f"Error al cargar calibración: {e}"
