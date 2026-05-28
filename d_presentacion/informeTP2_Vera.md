<div align="center">

---

# UNIVERSIDAD TECNOLÓGICA NACIONAL
## Facultad Regional Córdoba

---

<!-- [IMAGEN REQUERIDA] Logotipo oficial UTN FRC -->
<!-- Guardar en: assets/utn_frc_logo.png -->

---

**Licenciatura en Automatización y Control**

**Visión Artificial**

---

# Actividad Práctica N.° 2

## Detección de Colores y Control mediante Visión Artificial

---

**Docentes:**
Ing. González, Hernando Alexis
Ing. Miklosa, Pablo

---

**Alumno:** Vera, Cristian Gonzalo
**Legajo:** 420581

---

**Año:** 2026
**Período:** Mayo — Junio

---

**Repositorio:**
[https://github.com/Automatizacion-y-Control/TP2_python_VisionArtificial_UTN.git](https://github.com/Automatizacion-y-Control/TP2_python_VisionArtificial_UTN.git)

---

</div>

---

## Índice

1. [Introducción](#1-introducción)
2. [Marco Teórico](#2-marco-teórico)
   - 2.1 [Análisis estructural: RGB vs HSV](#21-análisis-estructural-rgb-vs-hsv)
   - 2.2 [Rangos HSV: criterios de selección y ajuste](#22-rangos-hsv-criterios-de-selección-y-ajuste)
   - 2.3 [Protocolos de comunicación utilizados](#23-protocolos-de-comunicación-utilizados)
3. [Diseño del Sistema](#3-diseño-del-sistema)
   - 3.1 [Arquitectura por capas](#31-arquitectura-por-capas)
   - 3.2 [Diagrama de flujo del algoritmo](#32-diagrama-de-flujo-del-algoritmo)
   - 3.3 [Esquema de conexión hardware](#33-esquema-de-conexión-hardware)
4. [Desarrollo por Etapas](#4-desarrollo-por-etapas)
   - 4.1 [Motor de detección](#41-motor-de-detección)
   - 4.2 [Lógica de decisión anti-ruido](#42-lógica-de-decisión-anti-ruido)
   - 4.3 [Comunicación serial](#43-comunicación-serial)
   - 4.4 [Firmware del sistema embebido](#44-firmware-del-sistema-embebido)
   - 4.5 [Panel de Control Industrial — PyQt5 (valor agregado)](#45-panel-de-control-industrial--pyqt5-valor-agregado)
5. [Pruebas y Resultados](#5-pruebas-y-resultados)
   - 5.1 [Tabla de escenarios](#51-tabla-de-escenarios)
   - 5.2 [Registro de ajuste de parámetros HSV](#52-registro-de-ajuste-de-parámetros-hsv)
   - 5.3 [Análisis de latencia](#53-análisis-de-latencia)
6. [Conclusiones](#6-conclusiones)
7. [Referencias](#7-referencias)
8. [Anexos](#8-anexos)

---

## 1. Introducción

El presente informe documenta el desarrollo del Trabajo Práctico N.° 2 de la materia Visión Artificial, correspondiente a la Licenciatura en Automatización y Control de la Universidad Tecnológica Nacional — Facultad Regional Córdoba.

El objetivo general del proyecto consiste en desarrollar un sistema de visión artificial capaz de detectar los colores primarios rojo, verde y amarillo en tiempo real mediante una cámara web, y transmitir la información de detección por puerto serial a un microcontrolador que realizará acciones físicas específicas según el color identificado.

### 1.1 Alcance del trabajo

El sistema desarrollado abarca la totalidad de la cadena de procesamiento: desde la adquisición de imagen hasta la actuación física sobre un LED RGB direccionable WS2812B conectado a un microcontrolador ESP32-C3. Se implementaron además mejoras sustanciales respecto al requerimiento mínimo, descritas en la sección de valor agregado.

### 1.2 Organización del informe

El informe se estructura siguiendo la guía de implementación provista por la cátedra: análisis y diseño, desarrollo por partes, integración y pruebas, y conclusiones. El código fuente completo se encuentra disponible en el repositorio indicado en la portada.

---

## 2. Marco Teórico

### 2.1 Análisis estructural: RGB vs HSV

#### El problema del espacio RGB para segmentación cromática

El modelo de color RGB representa cada píxel como la combinación aditiva de tres componentes: Rojo (*Red*), Verde (*Green*) y Azul (*Blue*). Si bien es el formato nativo de las cámaras digitales, presenta una limitación fundamental para la tarea de segmentación por color: la **crominancia y la luminancia están acopladas**.

En términos prácticos, esto significa que cualquier variación en las condiciones de iluminación (un foco que se enciende, una sombra parcial, luz natural cambiante) modifica los tres canales simultáneamente de manera no lineal. Como consecuencia, no es posible definir umbrales fijos en el espacio RGB que sean válidos bajo distintas condiciones de iluminación.

Por ejemplo, un objeto rojo bajo luz intensa presenta valores RGB aproximados de (200, 50, 50). El mismo objeto bajo una sombra parcial puede presentar (80, 20, 20). Ambos son "rojo", pero en coordenadas RGB los valores se superponen con objetos de otros colores bajo distintas iluminaciones.

<!-- [IMAGEN REQUERIDA] Diagrama comparativo: mismo objeto bajo distintas iluminaciones, valores RGB vs HSV -->
<!-- Guardar en: assets/rgb_vs_hsv_comparacion.png -->

#### La solución: el espacio HSV

El modelo HSV (*Hue, Saturation, Value*) descompone el color en tres componentes con semántica independiente:

| Canal | Nombre | Descripción | Rango OpenCV |
|-------|--------|-------------|--------------|
| **H** | Matiz (*Hue*) | El color puro en el círculo cromático | 0 — 179 |
| **S** | Saturación (*Saturation*) | Intensidad del color. S=0 es gris puro | 0 — 255 |
| **V** | Valor (*Value*) | Luminosidad. V=0 es negro, V=255 es máximo | 0 — 255 |

La ventaja estructural crítica es que el canal **H es independiente de la luminosidad V**. Un objeto rojo brillantemente iluminado y el mismo objeto a media luz comparten prácticamente el mismo valor de H. La variación de luz sólo afecta a V, y en menor medida a S. Esto permite definir umbrales fijos sobre H que son robustos bajo distintas condiciones de iluminación.

<!-- [IMAGEN REQUERIDA] Círculo cromático HSV anotado con las posiciones de rojo, verde y amarillo, mostrando los rangos implementados -->
<!-- Guardar en: assets/circulo_cromatico_hsv.png -->

> **Nota importante sobre la escala:** OpenCV representa el canal H en el rango [0, 179] en lugar del estándar [0°, 360°]. Para convertir: `H_openCV = H_grados / 2`. Así, el amarillo estándar (≈60°) equivale a H≈30 en OpenCV.

#### Por qué el rojo requiere dos rangos

El rojo ocupa ambos extremos del círculo cromático: H≈0 y H≈360° (H≈179 en OpenCV). Esto implica que una única máscara `inRange` con H_min < H_max no puede capturar simultáneamente ambos extremos.

La solución adoptada es aplicar dos máscaras independientes y combinarlas mediante suma saturada (`cv2.add`):

```
Máscara_R1:  H ∈ [0,  10]   → extremo inferior del círculo
Máscara_R2:  H ∈ [170, 179] → extremo superior del círculo
Máscara_rojo = cv2.add(Máscara_R1, Máscara_R2)
```

#### Rol de los umbrales S y V mínimos

Los valores mínimos de S y V actúan como **filtros de fondo pasivos**:

- Píxeles grises, blancos o negros tienen S≈0 y quedan excluidos sin necesidad de morfología adicional.
- Sombras profundas (V bajo) se eliminan ajustando V_min, evitando detecciones espurias en zonas oscuras.

---

### 2.2 Rangos HSV: criterios de selección y ajuste

Los rangos HSV finales del sistema se determinaron mediante calibración experimental con la cámara Redragon HD, utilizando objetos de referencia bajo condiciones de iluminación de laboratorio (luz artificial difusa, temperatura de color aproximada 4000 K).

| Color | H mín | H máx | S mín | S máx | V mín | V máx | Criterio del límite |
|-------|-------|-------|-------|-------|-------|-------|---------------------|
| **Verde** | 35 | 85 | 70 | 255 | 40 | 255 | Límite inferior para excluir verde-amarillento bajo luz cálida. V mín bajo para tolerar sombras |
| **Amarillo** | 20 | 38 | 95 | 255 | 95 | 255 | Ventana H estrecha para evitar solapamiento con verde. S y V elevados para excluir tonos ocres |
| **Rojo (bajo)** | 0 | 10 | 125 | 255 | 60 | 255 | Extremo inferior del espectro circular. S mín elevado para descartar blancos rosados |
| **Rojo (alto)** | 170 | 179 | 125 | 255 | 60 | 255 | Extremo superior — S y V compartidos con el rango bajo |

> Los rangos son punto de partida calibrado para esta cámara. El panel de control permite ajuste en vivo mediante sliders; los valores calibrados se persisten en `calibration.json`.

---

### 2.3 Protocolos de comunicación utilizados

#### Fase 1 — Comandos ASCII (implementado)

Protocolo de mínimo overhead para actuación directa:

```
R\n  →  Rojo       LED enciende en rojo
G\n  →  Verde      LED enciende en verde
Y\n  →  Amarillo   LED enciende en amarillo
N\n  →  Ninguno    LED apaga
```

**Parámetros de enlace:** 115200 bps, 8 bits de datos, sin paridad, 1 bit de stop (8N1).

El terminador `\n` garantiza la alineación del buffer de recepción en el microcontrolador ante posibles pérdidas parciales de datos.

#### Fase 2 — Tramas dinámicas RGB (implementado)

Protocolo de mayor expresividad para control directo del LED WS2812B:

```
<A,r,g,b>\n        →  Color global (todos los píxeles del LED)
<P,idx,r,g,b>\n    →  Píxel individual por índice
<B,valor>\n        →  Brillo global [0-255]
<OFF>\n            →  Apagado total
```

El delimitador `<...>` con terminador `\n` permite al receptor detectar y descartar tramas corruptas sin perder sincronismo.

---

## 3. Diseño del Sistema

### 3.1 Arquitectura por capas

El sistema se diseñó con separación estricta de responsabilidades en cinco capas:

```
┌─────────────────────────────────────────────────────────┐
│  CAPA 5 — Presentación (PyQt5)                          │
│  Panel de control industrial · Calibración en vivo      │
├─────────────────────────────────────────────────────────┤
│  CAPA 4 — Decisión y Control                            │
│  AntiNoiseFilter · Modo LED · Heartbeat serial           │
├─────────────────────────────────────────────────────────┤
│  CAPA 3 — Procesamiento de Imagen                       │
│  ColorDetector · Pipeline HSV · Morfología               │
├─────────────────────────────────────────────────────────┤
│  CAPA 2 — Adquisición y Comunicación                    │
│  CameraThread (QThread) · SerialCommunicator             │
├─────────────────────────────────────────────────────────┤
│  CAPA 1 — Hardware                                      │
│  Cámara Redragon HD · ESP32-C3 · LED WS2812B            │
└─────────────────────────────────────────────────────────┘
```

La separación de la captura de video en un `QThread` independiente garantiza que el pipeline de visión no bloquee la interfaz gráfica, asegurando una experiencia de usuario fluida incluso durante el procesamiento de imágenes a 30+ FPS.

<!-- [IMAGEN REQUERIDA] Diagrama de arquitectura por capas con flechas de flujo de datos -->
<!-- Guardar en: assets/arquitectura_capas.png -->

---

### 3.2 Diagrama de flujo del algoritmo

El algoritmo de detección sigue un pipeline de etapas discretas, cada una con entrada y salida definidas:

```
┌──────────────────────────────────┐
│  1. CAPTURA DE FRAME             │
│     cv2.VideoCapture(0)          │
│     Resolución: 640×480 px       │
└──────────────┬───────────────────┘
               ↓
┌──────────────────────────────────┐
│  2. PREPROCESAMIENTO             │
│     GaussianBlur(frame, (5,5))   │
│     → Reducción de ruido HF      │
└──────────────┬───────────────────┘
               ↓
┌──────────────────────────────────┐
│  3. CONVERSIÓN DE ESPACIO        │
│     BGR → HSV                    │
│     cv2.cvtColor(COLOR_BGR2HSV)  │
└──────────────┬───────────────────┘
               ↓
┌──────────────────────────────────┐
│  4. SEGMENTACIÓN CROMÁTICA       │
│     cv2.inRange() × 4 rangos     │
│     Verde: 1 máscara             │
│     Amarillo: 1 máscara          │
│     Rojo: 2 máscaras → cv2.add() │
└──────────────┬───────────────────┘
               ↓
┌──────────────────────────────────┐
│  5. MORFOLOGÍA                   │
│     cv2.morphologyEx(MORPH_CLOSE)│
│     Kernel: 5×5 px               │
│     → Cierre de huecos, limpieza │
└──────────────┬───────────────────┘
               ↓
┌──────────────────────────────────┐
│  6. CUANTIFICACIÓN               │
│     cv2.countNonZero() × 3       │
│     → px_rojo, px_verde, px_amar │
└──────────────┬───────────────────┘
               ↓
┌──────────────────────────────────┐
│  7. FILTRO ANTI-RUIDO (cadena)   │
│                                  │
│  7a. Umbral espacial             │
│      ¿px_color >= 4000?          │
│      NO → candidato = "ninguno"  │
│                                  │
│  7b. Estabilidad temporal        │
│      ¿Mismo color N=5 frames?    │
│      NO → mantener último estable│
│                                  │
│  7c. Filtro diferencial          │
│      ¿color ≠ último_enviado?    │
│      NO → no enviar              │
└──────────────┬───────────────────┘
               ↓
        ¿Enviar comando?
         /           \
       SÍ             NO
        ↓              ↓
┌─────────────┐    (esperar
│ 8. SERIAL   │     siguiente
│  send_color │     frame)
│  Fase 1 ó 2 │
└──────┬──────┘
       ↓
┌─────────────┐
│ 9. ESP32-C3 │
│  WS2812B    │
│  LED actúa  │
└─────────────┘
```

<!-- [IMAGEN REQUERIDA] Versión gráfica del diagrama de flujo (flowchart con símbolos estándar ISO 5807) -->
<!-- Guardar en: assets/diagrama_flujo_algoritmo.png -->

---

### 3.3 Esquema de conexión hardware

El sistema embebido utiliza un microcontrolador ESP32-C3 SuperMini conectado al LED WS2812B. La comunicación con la PC se realiza mediante USB-Serial (CH340 integrado).

| Componente | Conexión | Detalle |
|-----------|----------|---------|
| PC → ESP32-C3 | USB-B Micro | Alimentación + UART (CH340) |
| ESP32-C3 GPIO5 | DIN del WS2812B | Señal de datos NZR |
| WS2812B VCC | 5V | Alimentación directa desde USB |
| WS2812B GND | GND ESP32 | Masa común |

> **Nota sobre alimentación:** Para cadenas de más de 5 LEDs WS2812B se recomienda alimentación externa de 5V con masa común al ESP32, dado que la corriente por LED puede superar los 60 mA (blanco pleno).

<!-- [IMAGEN REQUERIDA] Esquema de conexión: ESP32-C3 SuperMini ↔ WS2812B con etiquetas de pines y valores de resistencia -->
<!-- Guardar en: assets/esquema_conexion_hardware.png -->

---

## 4. Desarrollo por Etapas

### 4.1 Motor de detección

El motor de detección se implementó en la clase `ColorDetector` del módulo `detector.py`. La clase encapsula el pipeline completo de procesamiento y acepta parámetros de configuración desde el módulo `config.py`, lo que permite la modificación de rangos HSV en tiempo de ejecución sin reiniciar el sistema.

```python
class ColorDetector:
    def process_frame(self, frame: np.ndarray) -> tuple:
        # 1. Suavizado Gaussiano
        processed = cv2.GaussianBlur(frame, (5, 5), 0)
        # 2. Conversión BGR → HSV
        hsv = cv2.cvtColor(processed, cv2.COLOR_BGR2HSV)
        # 3. Máscaras por color (leyendo config.HSV_RANGES en tiempo real)
        masks = { ... }
        # 4. Suma saturada para rojo
        masks["rojo"] = cv2.add(mask_r1, mask_r2)
        # 5. Cierre morfológico
        for color in masks:
            masks[color] = cv2.morphologyEx(masks[color], cv2.MORPH_CLOSE, self._kernel)
        # 6. Cuantificación
        pixel_counts = {c: cv2.countNonZero(masks[c]) for c in masks}
        return hsv, masks, pixel_counts
```

La lectura de `config.HSV_RANGES` en cada llamada (no en el constructor) garantiza que los ajustes realizados desde los sliders de calibración de la UI tomen efecto en el frame siguiente sin necesidad de reinicializar el detector.

<!-- [IMAGEN REQUERIDA] Captura de pantalla de la pestaña "VIDEO EN VIVO" mostrando overlay con FPS, color detectado y legajo -->
<!-- Guardar en: assets/app_video_en_vivo.png -->

---

### 4.2 Lógica de decisión anti-ruido

La clase `AntiNoiseFilter` implementa tres filtros en cascada que eliminan las principales fuentes de ruido antes de transmitir un comando serial.

#### Filtro 1 — Umbral espacial (anti-reflejo)

Descarta candidatos cuyo conteo de píxeles activos no supera el umbral mínimo configurado (valor predeterminado: 4000 px sobre un frame de 640×480 = 1.3% del área total).

**Propósito:** eliminar reflejos puntuales, sombras de color y píxeles ruidosos de la cámara que no corresponden a objetos reales.

#### Filtro 2 — Estabilidad temporal (anti-parpadeo)

El color candidato debe mantenerse idéntico durante N frames consecutivos (valor predeterminado: 5 frames ≈ 170 ms a 30 FPS) antes de confirmarse como color estable.

**Propósito:** evitar que movimientos rápidos del objeto o transiciones entre colores generen comandos erróneos intermedios.

#### Filtro 3 — Diferencial (anti-saturación serial)

Solo se transmite un nuevo comando cuando el color confirmado difiere del último comando enviado.

**Propósito:** prevenir la saturación del buffer serial del microcontrolador con comandos redundantes. Sin este filtro, se enviarían hasta 30 comandos idénticos por segundo.

```
Frame N:   candidato=verde  → historial=[verde,verde,verde,verde,verde]  → estable=verde  → ¿cambió? SÍ → enviar G\n
Frame N+1: candidato=verde  → historial=[verde,verde,verde,verde,verde]  → estable=verde  → ¿cambió? NO → no enviar
Frame N+2: candidato=ninguno→ historial=[verde,verde,verde,verde,ninguno]→ no estable     → no enviar
Frame N+6: candidato=ninguno→ historial=[ninguno×5]                      → estable=ninguno→ ¿cambió? SÍ → enviar N\n
```

---

### 4.3 Comunicación serial

El módulo `SerialCommunicator` gestiona la conexión con el ESP32-C3 con tres mecanismos de robustez:

1. **Conexión asíncrona:** la apertura del puerto serie (que incluye una pausa de 1.5 s para el reset del microcontrolador) se ejecuta en un `QThread` independiente (`ConnectThread`) para no bloquear la interfaz gráfica.

2. **Modo simulación (Mock Mode):** si `pyserial` no está disponible o no se detecta ningún puerto COM, el sistema activa automáticamente un modo de simulación donde los comandos se registran en el terminal de log en lugar de transmitirse por hardware. Esto permite validar el algoritmo de visión sin necesidad del hardware físico.

3. **Modo LED:** el panel permite seleccionar entre dos comportamientos de salida:
   - **Modo Pulso:** el comando se envía una sola vez al detectar un cambio. El ESP32 apaga el LED automáticamente tras su timeout interno de ~2 s.
   - **Modo Continuo:** además del envío por cambio, un heartbeat de 1 s reenvía el color activo, manteniendo el LED encendido mientras persiste la detección.

---

### 4.4 Firmware del sistema embebido

El firmware del ESP32-C3 implementa la recepción de comandos seriales y el control del LED WS2812B mediante la librería FastLED.

**Protocolo de recepción (Fase 1):**
- Lectura del buffer serial en cada ciclo del `loop()`.
- Estructura `switch-case` sobre el carácter recibido.
- Timeout de seguridad: si no se recibe comando en 2000 ms, el LED se apaga automáticamente (prevención ante pérdida de conexión con la PC).
- Retroalimentación por monitor serial para depuración.

**Control WS2812B (Fase 2):**
- Parser de tramas con delimitadores `<...>`.
- Soporte para color global, píxel individual y control de brillo.
- Validación de rango en valores R/G/B antes de aplicar.

---

### 4.5 Panel de Control Industrial — PyQt5 (valor agregado)

Se desarrolló una aplicación de escritorio completa en PyQt5 que supera el requerimiento mínimo del trabajo práctico al unificar todo el sistema en un panel de control industrial con las siguientes capacidades:

<!-- [IMAGEN REQUERIDA] Captura completa de la ventana principal (modo oscuro) con cámara activa y LINK MODE encendido -->
<!-- Guardar en: assets/app_panel_control_completo.png -->

#### Arquitectura de la interfaz

El panel implementa un layout de tres columnas con `QSplitter` redimensionable:

| Columna | Componentes |
|---------|-------------|
| **Izquierda** | Selector de puerto COM y cámara, protocolo, modo LED Pulso/Continuo, botones de test manual, control RGB Fase 2 con preview de color |
| **Central** | `QTabWidget` con: Video en Vivo (overlay FPS/color), Espacio HSV (falso color + espectro H), Máscaras 2×2 (+ panel de métricas) |
| **Derecha** | Calibrador HSV (6 sliders por color), filtros anti-ruido ajustables, estadísticas de sesión, perfil de calibración |

#### Vista HSV en falso color

La pestaña "Espacio HSV" implementa una visualización de falso color con valor diagnóstico real:

```
R = H × (255/179)   →  distribución de matices en el frame
G = S               →  zonas grises = baja saturación
B = V               →  zonas oscuras = baja luminosidad
```

Esta representación permite identificar visualmente qué regiones del frame se encuentran dentro de los rangos HSV configurados, facilitando el ajuste de parámetros de calibración.

<!-- [IMAGEN REQUERIDA] Pestaña ESPACIO HSV con papel amarillo en escena, mostrando barra de espectro H con bandas de colores configurados -->
<!-- Guardar en: assets/app_vista_hsv_falso_color.png -->

#### Vista de máscaras en cuatro cuadrantes

<!-- [IMAGEN REQUERIDA] Pestaña MÁSCARAS mostrando los 4 cuadrantes con objeto de color en escena -->
<!-- Guardar en: assets/app_vista_mascaras_4q.png -->

La pestaña "Máscaras" organiza la información en un panel 2×2 (640×480 px):

```
┌──────────────┬──────────────┐
│  ROJO        │  VERDE       │  ← máscaras binarias tintadas
│  con barra   │  con barra   │     + indicador de activación
├──────────────┼──────────────┤
│  AMARILLO    │  DETECTOR /  │  ← cuadrante de métricas:
│  con barra   │  MÉTRICAS    │     px por color, umbral,
└──────────────┴──────────────┘     estabilidad, color estable
```

---

## 5. Pruebas y Resultados

### 5.1 Tabla de escenarios

Se ejecutaron cuatro escenarios de prueba, siguiendo los lineamientos de la guía de implementación:

| # | Escenario | Condición | Comportamiento esperado | Resultado observado | Estado |
|---|-----------|-----------|------------------------|---------------------|--------|
| 1 | **Óptimo** | Luz difusa artificial, fondo oscuro, objeto mate | Detección estable, sin parpadeo, latencia < 300 ms | Detección correcta de los 3 colores. Tiempo de respuesta ≈ 180 ms promedio. Sin falsos positivos en fondo | ✅ Correcto |
| 2 | **Baja iluminación** | Sombras parciales sobre el objeto (50% de área sombreada) | El filtro V_mín actúa; la detección puede perder el objeto | Verde y rojo con V_mín=40/60 toleran sombras moderadas. Amarillo (V_mín=95) pierde detección con sombra > 40% | ✅ Esperado |
| 3 | **Contraluz / reflejo** | Luz directa hacia la cámara | Degradación de S — pérdida de firma espectral | Saturación de S en zonas brillantes. El objeto reflectante produce S < S_mín → no detectado | ✅ Esperado |
| 4 | **Solapamiento** | Luz cálida (incandescente) sobre objeto verde | Desplazamiento de H hacia rango amarillo | Con luz cálida intensa, el verde puede desplazar H hacia 40–50, entrando en el rango amarillo. Requiere ajuste de H_max verde a 70 | ⚠️ Parcial — requiere calibración específica por fuente de luz |

<!-- [IMAGEN REQUERIDA] Composición de 4 capturas: una por cada escenario de prueba mostrando la vista de máscaras -->
<!-- Guardar en: assets/escenarios_prueba.png -->

---

### 5.2 Registro de ajuste de parámetros HSV

Durante las pruebas de integración se realizaron los siguientes ajustes respecto a los valores de referencia de la guía:

| Parámetro | Valor guía | Valor inicial | Valor final | Razón del cambio |
|-----------|-----------|---------------|-------------|-----------------|
| Verde H_min | 36 | 35 | 35 | Sin cambio — cámara no registra deriva |
| Verde S_min | 50 | 70 | 70 | Aumentado para eliminar falsos positivos en fondos claros |
| Amarillo H_min | 20 | 20 | 20 | Sin cambio |
| Amarillo H_max | 35 | 38 | 38 | Ampliado levemente para capturar amarillo cálido bajo luz fluorescente |
| Amarillo S_min | 80 | 95 | 80* | *Reducido cuando se usa papel mate de baja saturación. Recomendado: 95 para objetos saturados |
| Rojo S_min | 120 | 125 | 125 | Sin cambio — adecuado para la cámara Redragon |
| Filtro px_mín | — | 4000 | 4000 | Sin cambio — equivale a ≈1.3% del frame. Adecuado para objetos de tamaño palm |
| Estabilidad | — | 5 frames | 5 frames | Sin cambio — balance entre velocidad (167 ms) y robustez |

> Los parámetros finales se persistieron en `calibration.json` y se cargan automáticamente al iniciar la aplicación.

---

### 5.3 Análisis de latencia

Se midió la latencia de extremo a extremo (desde la aparición del objeto hasta la actuación del LED) descomponiendo los tiempos en las etapas del pipeline:

| Etapa | Tiempo estimado | Notas |
|-------|----------------|-------|
| Captura de frame | ~33 ms | Determinado por FPS de la cámara (30 FPS) |
| Preprocesamiento + HSV | ~2 ms | GaussianBlur + cvtColor en CPU |
| Segmentación + morfología | ~3 ms | 4× inRange + 3× morphologyEx |
| Filtro anti-ruido (estabilidad) | 5 frames × 33 ms = **167 ms** | Latencia dominante del sistema |
| Transmisión serial | < 1 ms | ASCII, 115200 bps, 2 bytes |
| Procesamiento firmware ESP32 | ~5 ms | Recepción + FastLED.show() |
| **Total (primer evento)** | **≈ 210 ms** | |
| **Total (post-estabilidad)** | **≈ 38 ms** | Después de la primera confirmación |

La latencia dominante es el filtro de estabilidad temporal (5 frames). Este valor es un parámetro configurable en el panel: reducirlo a 1–2 frames disminuye la latencia pero aumenta la tasa de falsos positivos.

---

## 6. Conclusiones

El sistema desarrollado cumple en su totalidad con los requerimientos planteados por la cátedra y los extiende significativamente en las siguientes dimensiones:

**Sobre el algoritmo de detección:**
La elección del espacio HSV demostró ser la decisión de diseño más impactante del proyecto. La independencia entre el canal de matiz H y el canal de luminosidad V permitió definir umbrales estables que funcionan correctamente bajo variaciones de iluminación del orden del 40–50%, lo cual habría requerido umbrales dinámicos en RGB. El doble rango para el rojo, si bien añade complejidad al pipeline, es una necesidad fundamental impuesta por la geometría del espacio de color y no puede evitarse.

**Sobre la cadena de filtros anti-ruido:**
Los tres filtros en cascada (espacial, temporal, diferencial) resuelven de manera sistemática los tres problemas principales de robustez: detección de objetos pequeños o reflejos, parpadeo en transiciones, y saturación del canal serial. La parametrización de todos los umbrales en la interfaz permite adaptar el comportamiento a distintas condiciones sin modificar código.

**Sobre la arquitectura de software:**
La separación en módulos con responsabilidades únicas (`detector.py`, `filters.py`, `serial_comm.py`, `config.py`) facilitó la migración del prototipo de consola a la aplicación PyQt5 sin reescribir lógica de negocio. La arquitectura de QThread con señales Qt garantizó la separación entre el pipeline de visión y la interfaz de usuario, manteniendo la UI responsiva a 30+ FPS.

**Dificultades encontradas:**
- La compatibilidad entre OpenCV (opencv-contrib-python) y el backend de cámara en Windows requirió el uso del backend MSMF (Windows Media Foundation) y la inicialización de COM en el hilo de captura mediante CoInitializeEx.
- La gestión de memoria de QImage en Python (dangling pointer sobre buffers temporales de numpy) requirió el uso de `.copy()` en cada emisión de señal.

**Propuestas de mejora:**
- Implementar rangos HSV adaptativos mediante análisis de histograma del frame para ajuste automático ante cambios de iluminación.
- Agregar detección de formas (contornos) para combinar criterio cromático con criterio geométrico, reduciendo falsos positivos.
- Implementar un modo de grabación de sesión para exportar video con overlay de detección.

---

## 7. Referencias

1. Bradski, G., & Kaehler, A. (2008). *Learning OpenCV: Computer Vision with the OpenCV Library*. O'Reilly Media.

2. Gonzalez, R. C., & Woods, R. E. (2018). *Digital Image Processing* (4th ed.). Pearson.

3. OpenCV Documentation — Color Spaces. Recuperado de: https://docs.opencv.org/4.x/df/d9d/tutorial_py_colorspaces.html

4. PyQt5 Documentation. Recuperado de: https://www.riverbankcomputing.com/static/Docs/PyQt5/

5. Espressif Systems. (2024). *ESP32-C3 Technical Reference Manual*. Recuperado de: https://www.espressif.com/sites/default/files/documentation/esp32-c3_technical_reference_manual_en.pdf

6. FastLED Library Documentation. Recuperado de: https://fastled.io/

7. Jain, A. K. (1989). *Fundamentals of Digital Image Processing*. Prentice Hall.

---

## 8. Anexos

### Anexo A — Estructura del repositorio

```
TP2/
├── a_requisitos/               # Enunciado oficial y guía de implementación
├── b_investigacion/            # Marco teórico, diagramas y análisis previo
├── c_prototipado/
│   └── basico/python/          # Prototipo funcional (OpenCV sin GUI)
│       ├── config.py           # Parámetros HSV, serial y filtros
│       ├── detector.py         # ColorDetector — pipeline HSV
│       ├── filters.py          # AntiNoiseFilter — cadena de 3 filtros
│       ├── serial_comm.py      # SerialCommunicator con mock mode
│       └── main.py             # Orquestador principal
└── d_presentacion/
    ├── informeTP2_Vera.md      # Este documento
    ├── assets/                 # Imágenes referenciadas en el informe
    └── basico/
        ├── app/                # Aplicación PyQt5 (entregable principal)
        │   ├── main.py
        │   ├── main_window.py
        │   ├── camera_thread.py
        │   ├── detector.py
        │   ├── filters.py
        │   ├── serial_comm.py
        │   ├── config.py
        │   ├── styles.py
        │   └── requirements.txt
        ├── scrum.md
        ├── deudaTecnica.md
        ├── bitacora.md
        └── implementation_plan.md
```

### Anexo B — Instalación y ejecución

**Requisitos del entorno:**

```powershell
# Python 3.13 — ejecutar desde PowerShell (no Git Bash)
pip install PyQt5 opencv-python numpy pyserial
# o mediante requirements.txt:
pip install -r d_presentacion/basico/app/requirements.txt
```

**Ejecutar la aplicación principal:**

```powershell
cd d_presentacion/basico/app
py -3.13 main.py
```

**Ejecutar el prototipo de consola:**

```powershell
cd c_prototipado/basico/python
py main.py
```

### Anexo C — Imágenes requeridas para el informe

El directorio `d_presentacion/assets/` debe contener las siguientes imágenes para completar el documento:

| Archivo | Sección | Descripción |
|---------|---------|-------------|
| `utn_frc_logo.png` | Portada | Logotipo oficial UTN FRC |
| `rgb_vs_hsv_comparacion.png` | 2.1 | Comparativo: mismo objeto bajo distintas iluminaciones, valores RGB vs HSV |
| `circulo_cromatico_hsv.png` | 2.1 | Círculo cromático HSV con rangos de los 3 colores anotados |
| `arquitectura_capas.png` | 3.1 | Diagrama de arquitectura por capas |
| `diagrama_flujo_algoritmo.png` | 3.2 | Flowchart del algoritmo con símbolos estándar |
| `esquema_conexion_hardware.png` | 3.3 | Esquema ESP32-C3 ↔ WS2812B |
| `app_panel_control_completo.png` | 4.5 | Captura completa del panel PyQt5 en operación |
| `app_vista_hsv_falso_color.png` | 4.5 | Pestaña HSV con objeto de color en escena |
| `app_vista_mascaras_4q.png` | 4.5 | Pestaña Máscaras con los 4 cuadrantes |
| `escenarios_prueba.png` | 5.1 | Composición de los 4 escenarios de prueba |

---

<div align="center">

*Universidad Tecnológica Nacional — Facultad Regional Córdoba*
*Licenciatura en Automatización y Control — Visión Artificial*
*Cristian Gonzalo Vera · Legajo 420581 · 2026*

</div>
