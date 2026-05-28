# Solución Profesional de Presentación — Visión Artificial & Control (TP2)

Este directorio contiene el entregable avanzado de presentación para el Trabajo Práctico Nº2. Consiste en una aplicación de escritorio industrial desarrollada en Python utilizando **PyQt5**, que unifica el control de la cámara, procesamiento en tiempo real, calibración y comunicación serie con el microcontrolador.

---

## 1. Estructura de la Carpeta `basico/`

El módulo se organiza de la siguiente manera:

```text
d_presentacion/basico/
├── README.md         # Este archivo
├── scrum.md          # Gestión ágil del proyecto (Épicas, Sprints e Historias de Usuario)
├── deudaTecnica.md   # Registro sistemático de la deuda técnica
├── bitacora.md       # Hoja de ruta de desarrollo y diario de sprints
├── micro/            # Documentación e integración del firmware del ESP32-C3
└── app/              # Código fuente de la aplicación de escritorio PyQt5
```

---

## 2. Requisitos de la Aplicación de Escritorio (`app/`)

La aplicación está diseñada bajo el estándar de un panel de control industrial:

1. **Gestión de Puertos:** Escaneo automático y manual del puerto COM para detectar la placa.
2. **Control Remoto & Manual:** Sliders y botones para encender el LED WS2812B de forma manual (probando la conexión) antes de activar la cámara.
3. **Calibración HSV en Vivo:** Trackbars para ajustar los rangos mínimo y máximo del verde, amarillo y rojo en tiempo real, viendo el impacto inmediato sobre las máscaras binarias.
4. **Link de Detección:** Activación del modo automático (cámara web -> procesamiento -> envío serie).
5. **Estadísticas e Informes:** Contadores de detecciones, gráficos de barra/línea históricos y generación de informes de latencia y precisión para la defensa del proyecto.
