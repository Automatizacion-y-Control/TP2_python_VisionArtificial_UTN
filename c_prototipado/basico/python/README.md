# Módulo de Prototipado en Python — Visión Artificial (TP2)

Este directorio contiene el desarrollo práctico en Python para el procesamiento de imágenes, segmentación en espacio HSV, filtrado de ruido y comunicación serial para el Trabajo Práctico Nº2.

---

## 1. Estructura de Archivos y Arquitectura Modular

El backend en Python está desacoplado en componentes con responsabilidades específicas:

```text
c_prototipado/basico/python/
├── config.py         # Configuración y calibración (HSV, filtros, puerto serie)
├── detector.py       # Algoritmo de procesamiento y generación de máscaras (OpenCV)
├── filters.py        # Filtro en cadena anti-ruido (espacial, temporal, diferencial)
├── serial_comm.py    # Conectividad serie física con fallback a modo simulación (Mock)
├── main.py           # Orquestador del bucle principal de captura y GUI
└── protocoloSerie.md # Especificación detallada de tramas e integración con ESP32
```

### Flujo Lógico del Código (Pipeline)
```text
 Cámara Web 
      │ (BGR Frame)
      ▼
┌──────────────┐      ┌──────────────┐
│  detector.py │ ───> │  filters.py  │
└──────────────┘      └──────┬───────┘
  • Blur Gaussiano           │ (confirmed_color, should_send)
  • Conversión HSV           ▼
  • Máscaras binarias ┌──────────────┐      ┌─────────────────┐
  • Cierre morfológico│   main.py    │ ───> │  serial_comm.py │
  • countNonZero      └──────────────┘      └─────────────────┘
                        • Bucle principal     • Transmisión física
                        • FPS y GUI           • Latido (heartbeat)
```

---

## 2. Descripción de Módulos

### `config.py`
Centraliza todas las variables de control. Aquí se configuran los rangos de calibración de HSV para cada color (`verde`, `amarillo`, `rojo`), los parámetros de los filtros temporales de estabilidad ($N$ frames) y el puerto de comunicación física (por defecto `COM11`).

### `detector.py`
Contiene la clase `ColorDetector`. Recibe el frame capturado, aplica un suavizado Gaussiano para mitigar el ruido de alta frecuencia del sensor, y realiza la segmentación mediante `cv2.inRange()`. Debido a la naturaleza circular del canal de Tono (Hue), une las dos máscaras del rojo mediante la suma saturada de OpenCV (`cv2.add()`). Aplica un cierre morfológico con un kernel estructurado de 5x5 para sellar micro-perforaciones e irregularidades.

### `filters.py`
Contiene la clase `AntiNoiseFilter` que implementa tres filtros en cadena:
1. **Filtro Espacial:** Descarta detecciones cuyo conteo de píxeles activos en la máscara sea menor a `FILTER_MIN_PIXELS` (4000 px).
2. **Filtro Temporal:** Registra un historial de los últimos $N=5$ frames. Si no hay acuerdo absoluto en el historial, mantiene el último estado válido para evitar parpadeos visuales.
3. **Filtro Diferencial:** Detecta variaciones en el color estable confirmado, emitiendo una señal de transmisión serial únicamente si el estado cambia.

### `serial_comm.py`
Contiene la clase `SerialCommunicator`. Intenta abrir el puerto configurado (ej: `COM11`). Si falla, escanea el bus de Windows en búsqueda de puertos alternativos. Si no encuentra hardware, activa automáticamente el **Modo Simulación (Mock)** imprimiendo las tramas de salida directamente en la consola para depuración.

### `main.py`
Es el punto de entrada que orquestador del sistema. Administra la cámara (`cv2.VideoCapture`), actualiza la interfaz visual en vivo con un overlay de depuración en la ventana principal, rotula y apila las tres máscaras binarias de color en una vista comparativa horizontal, y envía un **latido de corazón (heartbeat) cada 1.0 segundo** al puerto serie si el color detectado permanece estable para evitar que el temporizador de inactividad del ESP32 (2000 ms) apague los LEDs.

---

## 3. Instrucciones de Ejecución

### Requisitos Previos
Asegúrate de contar con las dependencias instaladas en tu entorno de Python:
```bash
pip install numpy opencv-python pyserial
```

### Ejecutar el Prototipo
Ejecuta el script principal desde la raíz del espacio de trabajo:
```powershell
py c_prototipado/basico/python/main.py
```
*(Para salir del programa, presiona la tecla **`q`** sobre cualquiera de las ventanas abiertas de OpenCV).*
