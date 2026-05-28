# TP2 — Detección de Colores y Control mediante Visión Artificial

<div align="center">

# Introducción a la Visión Artificial
## Licenciatura en Automatización y Control
### Universidad Tecnológica Nacional — Facultad Regional Córdoba

---

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?style=for-the-badge&logo=opencv)
![ESP32-S3](https://img.shields.io/badge/ESP32--S3-ESP--IDF-red?style=for-the-badge&logo=espressif)
![Platform](https://img.shields.io/badge/Platform-VSCode-007ACC?style=for-the-badge&logo=visualstudiocode)
![Framework](https://img.shields.io/badge/Framework-ESP--IDF-black?style=for-the-badge)
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

# Descripción general

El presente proyecto desarrolla un sistema de visión artificial capaz de detectar colores en tiempo real mediante procesamiento digital de imágenes utilizando OpenCV.

El sistema implementa:

- captura de video mediante cámara web,
- segmentación cromática en espacio HSV,
- detección de colores primarios,
- lógica de decisión anti-ruido,
- comunicación serial,
- y actuación física mediante un microcontrolador ESP32-S3.

---

# Objetivo del proyecto

Desarrollar un sistema capaz de:

1. Capturar imágenes en tiempo real.
2. Detectar colores:
   - rojo,
   - verde,
   - amarillo.
3. Procesar información utilizando OpenCV.
4. Determinar el color predominante.
5. Transmitir comandos hacia un sistema embebido.
6. Actuar físicamente mediante un LED RGB WS2812B.

---

## Arquitectura general

```text
Cámara Web
    ↓
Python + OpenCV
    ↓
Procesamiento HSV
    ↓
Detección de color
    ↓
Comunicación Serial
    ↓
ESP32-S3
    ↓
LED WS2812B
```

---

## Tecnologías utilizadas

### Software
- Python 3.11
- OpenCV
- NumPy
- PySerial
- Visual Studio Code
- ESP-IDF

### Hardware
- Cámara Redragon HD 720P
- ESP32-S3 SuperMini
- LED RGB direccionable WS2812B

---

## Estructura del proyecto

El proyecto está organizado en las siguientes carpetas:

```text
tp2_vision/
├── a_requisitos/
├── b_investigacion/
├── c_prototipado/
└── d_presentacion/
```

### Organización general

| Carpeta | Contenido |
| --- | --- |
| `a_requisitos` | Contrato y requerimientos oficiales |
| `b_investigacion` | Marco teórico y análisis |
| `c_prototipado` | Desarrollo e implementación |
| `d_presentacion` | Material final e informe |

---

## Estado actual del proyecto

- [x] Análisis del problema
- [x] Diseño del sistema
- [x] Investigación HSV
- [ ] Captura de video
- [ ] Segmentación HSV
- [ ] Detección de colores
- [ ] Comunicación serial
- [ ] Firmware ESP32-S3
- [ ] Integración completa
- [ ] Validación experimental
- [ ] Informe técnico final

---

## Objetivo académico

Este trabajo práctico busca aplicar conceptos de:

- visión artificial,
- procesamiento digital de imágenes,
- sistemas embebidos,
- comunicación serial,
- y automatización inteligente.

### Universidad

Universidad Tecnológica Nacional  
Facultad Regional Córdoba  
Licenciatura en Automatización y Control  

### Materia

Introducción a la Visión Artificial  

### Autor

Cristian Gonzalo Vera  
Legajo: 420581