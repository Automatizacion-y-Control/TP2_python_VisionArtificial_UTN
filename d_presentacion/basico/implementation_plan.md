# Plan de Implementación — Panel de Control Industrial PyQt5 (TP2)

Este plan describe la arquitectura y el diseño técnico para migrar el prototipo básico a una aplicación de escritorio profesional en **PyQt5** con diseño oscuro industrial, ubicada en `d_presentacion/basico/app/`.

---

## Decisiones de Diseño y Arquitectura

> [!IMPORTANT]
> * **Hilo Secundario para Cámara (`QThread`):** La captura de OpenCV y el procesamiento HSV correrán en un hilo secundario (`CameraThread`) para evitar congelar la interfaz de usuario (GUI) principal y asegurar un framerate fluido (30+ FPS).
> * **Diseño Visual QSS (Estética Industrial):** La aplicación adoptará una paleta de colores oscuros inspirada en paneles SCADA modernos (`#0C1017` base, `#131A24` paneles, `#00D4FF` acentos de selección, y LEDs indicadores parpadeantes con efectos de sombra).
> * **Estructura Autónoma:** La carpeta `d_presentacion/basico/app/` será completamente autocontenida para facilitar su empaquetado y defensa frente a la cátedra.

---

## Estructura de Archivos Propuesta

Se creará el módulo de la aplicación en [d_presentacion/basico/app/](file:///d:/UTN/Licenciaturas/Automatizacion%20y%20Control/Nivel%202/1er%20Cuatrimestre/7%20Introduccion%20a%20la%20vision%20artificial/3%20Entregas/TP2/d_presentacion/basico/app/) con la siguiente arquitectura:

```text
d_presentacion/basico/app/
├── main.py            # Inicialización de QApplication y ejecución de la ventana
├── main_window.py     # Ventana principal (Organización de layouts, pestañas y paneles)
├── camera_thread.py   # QThread para captura de frames de video y procesamiento
├── styles.py          # Definición de hojas de estilo QSS e iconos empotrados
├── serial_comm.py     # Lógica serie PyQt-compatible (puertos físicos y modo simulado)
├── detector.py        # Detector HSV (clonado del prototipo validado)
├── filters.py         # Filtro anti-ruido (clonado del prototipo validado)
└── config.py          # Parámetros del panel y rutas persistentes
```

---

### Detalles del Desarrollo por Componente

#### 1. Hilo de Cámara ([camera_thread.py](file:///d:/UTN/Licenciaturas/Automatizacion%20y%20Control/Nivel%202/1er%20Cuatrimestre/7%20Introduccion%20a%20la%20vision%20artificial/3%20Entregas/TP2/d_presentacion/basico/app/camera_thread.py))
* Heredará de `QThread`.
* Bucle de captura continuo con `cv2.VideoCapture`.
* Llamará a `detector.py` y `filters.py` frame a frame.
* Emitirá señales Qt:
  * `frame_ready(QImage)`: Para pintar en el visor principal.
  * `hsv_ready(QImage)`: Para la pestaña de depuración HSV.
  * `masks_ready(QImage)`: Para la pestaña de máscaras combinadas.
  * `stats_updated(dict)`: Con los conteos de píxeles para actualizar los gráficos de la GUI.
  * `color_confirmed(str)`: Emitida al confirmar estabilidad de color.

#### 2. Ventana de Control ([main_window.py](file:///d:/UTN/Licenciaturas/Automatizacion%20y%20Control/Nivel%202/1er%20Cuatrimestre/7%20Introduccion%20a%20la%20vision%20artificial/3%20Entregas/TP2/d_presentacion/basico/app/main_window.py))
* **Barra Superior:** Título de la UTN, legajo, LED de estado de conexión serial y botón de Link.
* **Layout de Tres Columnas:**
  * **Columna Izquierda (Conexión y Test Manual):** Combo selector de puertos COM detectados en vivo, botón de conectar, y zona de "Test Manual" (botones de color y sliders RGB dinámicos para Phase 2).
  * **Columna Central (Visualizador Gráfico):** Un `QTabWidget` con tres pestañas:
    1. *Video en Vivo:* Con overlay semitransparente, FPS e indicador visual.
    2. *Espacio HSV:* Vista en color falso HSV.
    3. *Máscaras:* Vista side-by-side de las máscaras binarias rotuladas.
  * **Columna Derecha (Calibrador e Históricos):** Controles deslizantes para ajustar en tiempo real el $H_{min}, H_{max}, S_{min}, V_{min}$ de cada color, umbrales de píxeles, estabilidad y botón para guardar/cargar configuración.
* **Barra Inferior:** Terminal integrada de log que muestra comandos enviados y respuestas.

#### 3. Estilos y Temas ([styles.py](file:///d:/UTN/Licenciaturas/Automatizacion%20y%20Control/Nivel%202/1er%20Cuatrimestre/7%20Introduccion%20a%20la%20vision%20artificial/3%20Entregas/TP2/d_presentacion/basico/app/styles.py))
* Hoja de estilos QSS unificada.
* Define bordes redondeados, degradados lineales, estados `:hover`, `:pressed` y `:disabled` con colores reactivos.
* Efectos de brillo de sombra (`QGraphicsDropShadowEffect`) para botones activos y LEDs de visualización.

---

## Plan de Verificación

### Pruebas de Ejecución Manual
1. **Lanzamiento de Aplicación:**
   ```powershell
   py d_presentacion/basico/app/main.py
   ```
2. **Auditoría de Interfaz:** Verificar que se renderice la interfaz oscura sin errores gráficos y que el escáner de puertos identifique correctamente el puerto `COM11` (o en su defecto `COM1` o modo simulador).
3. **Validación de Calibración:** Modificar los sliders en la columna derecha y verificar que las máscaras binarias de la pestaña central se alteren dinámicamente.
4. **Verificación de Enlace:** Activar el "Modo Link" y validar en la consola de logs inferior que se emitan los bytes de color y los heartbeats cada 1.0 segundo.
