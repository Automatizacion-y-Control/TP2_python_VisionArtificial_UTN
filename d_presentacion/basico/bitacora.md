# Bitácora de Desarrollo — TP2 Desktop Dashboard

Este documento registra cronológicamente las actividades, decisiones y estados de avance en la implementación de la aplicación de escritorio PyQt5.

---

## 1. Estado de Avance General

* **Fase de Investigación (Parte 1):** `100% Completado`
  * Definición de la teoría de RGB vs HSV.
  * Establecimiento del diagrama de flujo.
  * Calibración teórica inicial de colores.
* **Fase de Prototipado Básico (Parte 2, 3, 4, 5 y 7 básica):** `100% Completado`
  * Módulos de Python (`config.py`, `detector.py`, `filters.py`, `serial_comm.py`, `main.py`).
  * Validación funcional en simulación y calibración en vivo (Verde, Amarillo, Rojo).
  * Redacción del protocolo serial (`protocoloSerie.md`).
* **Fase de Aplicación de Presentación (PyQt5 App):** `100% Completado`
  * Planificación SCRUM, definición de historias de usuario y registro de deudas.
  * Implementación completa de los 4 sprints en `d_presentacion/basico/app/`.

---

## 2. Diario de Desarrollo y Hoja de Ruta

### [28/05/2026] — Implementación Completa de la App PyQt5 (Todos los Sprints)

* **Hecho:**
  * Se creó la estructura completa `d_presentacion/basico/app/` con 8 módulos Python.
  * **Sprint 1 (Conectividad y Base UI):** Ventana industrial dark theme, escaneo de puertos COM, selector de cámara, conexión serial asíncrona (sin congelar UI), botones de test manual R/G/Y/N.
  * **Sprint 2 (Visión en GUI):** `CameraThread` (QThread) con 3 vistas integradas en `QTabWidget` (Video en Vivo, Espacio HSV, Máscaras). Overlay con FPS, color estable, candidato.
  * **Sprint 3 (Calibrador HSV):** 6 sliders por color (H_min/max, S_min/max, V_min/max). Rojo con doble rango correctamente expuesto. Filtros ajustables en vivo. Persistencia JSON (`calibration.json`).
  * **Sprint 4 (Link Mode + Estadísticas):** Botón LINK MODE con efecto de brillo. Contadores de detección, barras de proporción, tiempo de sesión. Exportación de reporte `.txt`.
  * **Correcciones de diseño aplicadas:** 6 sliders en calibrador (no 4), selector de cámara desde Sprint 1, terminal con timestamps y colores diferenciados, LED indicadores con `QGraphicsDropShadowEffect`.
  * **Dependencias:** PyQt5 5.15.11, opencv-python 4.13, numpy 2.4, pyserial 3.5 — instaladas en Python 3.13.
* **Por hacer:**
  * Defensa del TP ante la cátedra — demo con hardware ESP32-C3 y WS2812B.

---

### [27/05/2026] — Alineación e Inicialización de la Aplicación Profesional
* **Hecho:**
  * Se auditó el prototipo modular básico y se realizaron los ajustes finos HSV para los tres colores solicitados.
  * Se definió el alcance del entregable de presentación: migrar la solución a una aplicación de escritorio industrial con PyQt5.
  * Se crearon los archivos de control ágil en `d_presentacion/basico/`: `README.md`, `scrum.md`, `deudaTecnica.md` y `bitacora.md`.
* **Haciendo:**
  * Estructuración del plan de implementación para la Épica 1 y el Sprint 1 (Base UI y Conexión Serial).
* **Por hacer:**
  * Diseñar la ventana principal en PyQt5 usando hojas de estilo (QSS) con estética oscura (inspirada en la paleta industrial de GitHub/Discord).
  * Desarrollar la lógica del escáner de puertos COM para detectar y conectarse al ESP32-C3 (`COM11`).
  * Implementar botones de control de color manuales para probar la actuación en el WS2812B de forma directa.
