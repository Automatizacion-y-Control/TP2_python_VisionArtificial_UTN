# TP2 — Detección de Colores y Control mediante Visión Artificial

<div align="center">

# Introducción a la Visión Artificial
## Licenciatura en Automatización y Control
### Universidad Tecnológica Nacional — Facultad Regional Córdoba

---

![Version](https://img.shields.io/badge/Release-v1.0.0-brightgreen?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15-41CD52?style=for-the-badge&logo=qt)
![OpenCV](https://img.shields.io/badge/OpenCV-4.13-green?style=for-the-badge&logo=opencv)
![ESP32](https://img.shields.io/badge/ESP32--C3-Firmware-red?style=for-the-badge&logo=espressif)
![License](https://img.shields.io/badge/Academic_Project-UTN_FRC-orange?style=for-the-badge)

---

## Trabajo Práctico Nº2
### Sistema de Detección de Colores mediante Visión Artificial y Control Embebido

---

### Alumno
## Cristian Gonzalo Vera

### Legajo
## 420581

---

### Año Lectivo
## 2026

### Período
## Mayo / Junio

</div>

---

## Descripción general

Sistema de visión artificial que detecta colores en tiempo real mediante procesamiento digital de imágenes (OpenCV + espacio HSV) y actúa físicamente sobre un LED RGB direccionable WS2812B conectado a un microcontrolador ESP32-C3, todo orquestado desde un **panel de control industrial** desarrollado en PyQt5.

---

## Arquitectura del sistema

```text
Cámara Web (Redragon HD)
        ↓
CameraThread (QThread)
        ↓  BGR → HSV → inRange → morfología
ColorDetector + AntiNoiseFilter
        ↓  filtro espacial → temporal → diferencial
SerialCommunicator  ←──── Modo LED: Pulso / Continuo
        ↓  Fase 1: R/G/Y/N\n  |  Fase 2: <A,r,g,b>\n
ESP32-C3 + WS2812B
```

---

## Panel de Control Industrial (PyQt5)

La aplicación de escritorio unifica todo el sistema en una interfaz de **tema oscuro/claro** con layout de tres columnas:

| Columna | Contenido |
|---------|-----------|
| **Izquierda** | Conexión serial, selector de cámara, protocolo, modo LED (Pulso/Continuo), test manual, control RGB Fase 2 |
| **Central** | Video en vivo · Espacio HSV (falso color + métricas) · Máscaras 2×2 |
| **Derecha** | Calibrador HSV (6 sliders por color) · Filtros anti-ruido · Estadísticas · Perfil de calibración |

### Características principales

- **Conexión serial asíncrona** — no bloquea la UI durante la negociación con el ESP32
- **Vista HSV en falso color** — muestra H/S/V como R/G/B con barra de espectro y rangos calibrados superpuestos
- **Panel de máscaras 2×2** — 3 cuadrantes de máscara + cuadrante de métricas en tiempo real
- **Modo LED Pulso/Continuo** — seleccionable en UI; modo continuo usa heartbeat de 1 s
- **Calibrador HSV completo** — 6 sliders por color (H min/max, S min/max, V min/max); rojo expone doble rango correctamente
- **Persistencia JSON** — guarda y carga perfiles de calibración con validación de rangos
- **Toggle Tema Claro/Oscuro** — botón ☀/🌙 en el header; paleta oscura industrial / paleta clara Fluent
- **Terminal de log** — timestamped, color-coded por nivel (INFO/OK/TX/WARN/ERROR)
- **Exportación de reporte** — genera `.txt` con estadísticas de sesión y calibración activa

---

## Protocolo Serial

### Fase 1 — Comandos ASCII
```
R\n  →  Rojo       (LED rojo)
G\n  →  Verde      (LED verde)
Y\n  →  Amarillo   (LED amarillo)
N\n  →  Ninguno    (LED apagado)
```

### Fase 2 — Tramas dinámicas RGB
```
<A,r,g,b>\n        →  Color global todos los LEDs
<P,idx,r,g,b>\n    →  LED individual por índice
<B,value>\n        →  Brillo global (0-255)
<OFF>\n            →  Apagado total
```

**Parámetros:** 115200 bps · 8N1 · Timeout ESP32: ~2 s

---

## Estructura del proyecto

```text
TP2/
├── a_requisitos/               # Enunciado y requerimientos oficiales
├── b_investigacion/            # Marco teórico: RGB vs HSV, diagrama de flujo
├── c_prototipado/
│   └── basico/python/          # Prototipo funcional OpenCV (sin GUI)
│       ├── config.py
│       ├── detector.py
│       ├── filters.py
│       ├── serial_comm.py
│       └── main.py
└── d_presentacion/
    └── basico/
        ├── app/                # Aplicación de escritorio PyQt5 ← ENTREGABLE PRINCIPAL
        │   ├── main.py
        │   ├── main_window.py
        │   ├── camera_thread.py
        │   ├── detector.py
        │   ├── filters.py
        │   ├── serial_comm.py
        │   ├── config.py
        │   ├── styles.py
        │   └── requirements.txt
        ├── README.md
        ├── scrum.md
        ├── deudaTecnica.md
        ├── bitacora.md
        └── implementation_plan.md
```

---

## Instalación y ejecución

### Requisitos

- Python 3.13 (recomendado) — **no usar Git Bash, usar PowerShell o CMD**
- Dependencias:

```powershell
pip install PyQt5 opencv-python numpy pyserial
```

O desde el archivo de requisitos:

```powershell
pip install -r d_presentacion/basico/app/requirements.txt
```

### Ejecutar la aplicación

```powershell
cd d_presentacion/basico/app
py -3.13 main.py
```

### Ejecutar el prototipo básico (sin GUI)

```powershell
cd c_prototipado/basico/python
py main.py
```

---

## Estado del proyecto — v1.0.0

- [x] Investigación HSV y comparativa RGB vs HSV
- [x] Diagrama de flujo del sistema
- [x] Prototipo Python con OpenCV (detector + filtros + serial)
- [x] Protocolo serial documentado (Fase 1 y Fase 2)
- [x] Aplicación de escritorio PyQt5 completa (4 sprints)
- [x] Calibrador HSV en vivo (6 sliders por color)
- [x] Vista HSV en falso color con espectro y métricas
- [x] Vista de máscaras en 4 cuadrantes con panel de métricas
- [x] Modo LED Pulso / Continuo
- [x] Toggle tema oscuro / claro
- [x] Persistencia de calibración (JSON)
- [x] Exportación de reporte de sesión (.txt)
- [x] Comunicación serial física con ESP32-C3 validada
- [x] Actuación sobre LED WS2812B validada

---

## Tecnologías utilizadas

### Software
| Tecnología | Versión | Uso |
|-----------|---------|-----|
| Python | 3.13 | Lenguaje principal |
| PyQt5 | 5.15.11 | Interfaz gráfica de escritorio |
| OpenCV | 4.13 | Captura y procesamiento de imágenes |
| NumPy | 2.4 | Operaciones matriciales sobre frames |
| PySerial | 3.5 | Comunicación con ESP32 |

### Hardware
| Componente | Descripción |
|-----------|-------------|
| Cámara Redragon HD | Webcam USB 720p, índice 0 |
| ESP32-C3 SuperMini | Microcontrolador con firmware de control LED |
| LED WS2812B | LED RGB direccionable, protocolo propio |

---

## Universidad

Universidad Tecnológica Nacional — Facultad Regional Córdoba
Licenciatura en Automatización y Control
Materia: Introducción a la Visión Artificial
Autor: Cristian Gonzalo Vera · Legajo: 420581
