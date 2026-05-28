# Guía de Implementación — TP2: Detección de Colores y Control
**Visión Artificial | UTN FRC | Licenciatura en Automatización y Control**
**Docentes:** Ing. González, Hernando Alexis | Ing. Miklosa, Pablo
**Fecha límite:** 12/06/2025

---

## Lectura del contrato

El PDF oficial define el requerimiento mínimo: **cámara web → Python/OpenCV → puerto serial → Arduino → LEDs**. Ese es el piso. La rúbrica no cambia:

| Criterio | Peso |
|---|---|
| Funcionamiento técnico | 40% |
| Calidad de implementación | 30% |
| Documentación y análisis | 20% |
| Creatividad y valor agregado | 10% |

El 90% de la nota se gana con solidez técnica y documentación rigurosa. El 10% restante con la arquitectura avanzada. No al revés.

---

## Estrategia general

Implementar el núcleo obligatorio correctamente y extenderlo hacia la arquitectura distribuida. Ambas capas comparten el mismo algoritmo de detección — no es trabajo doble.

```
NÚCLEO (90% de la nota)
    Cámara USB → OpenCV → pyserial → Arduino → LEDs discretos

EXTENSIÓN (10% + diferenciación en defensa)
    Cámara celular → FastAPI/WebSocket → OpenCV headless → MQTT → ESP32 + WS2812B
```

---

## Parte 1 — Análisis y Diseño

### Qué hay que producir

- Análisis escrito de RGB vs HSV: no descriptivo, sino estructural. El profe quiere entender que comprendés *por qué* RGB falla, no solo que HSV es mejor.
- Tabla de rangos HSV para los tres colores, con justificación de cada límite.
- Diagrama de flujo completo del sistema: desde la captura hasta la actuación física.

### Decisiones de diseño a justificar

**Por qué HSV:** en RGB, la crominancia y la luminancia están acopladas. Cualquier cambio de luz modifica los tres canales simultáneamente — no se pueden definir umbrales fijos. HSV desacopla el matiz (H) de la intensidad (V), permitiendo umbrales estables bajo distintas condiciones de iluminación.

**Por qué rojo tiene dos rangos:** su espectro cruza el origen del modelo HSV (0°/360°). Una sola máscara no puede capturar ambos extremos del círculo cromático. Las dos máscaras se unen por suma algebraica.

**Por qué S y V mínimos > 0:** actúan como filtro de fondo. Píxeles grises, negros u oscuros tienen S y V bajos y quedan excluidos automáticamente, sin necesidad de morfología adicional para el ruido básico.

### Rangos HSV de referencia

| Color | Rango mínimo | Rango máximo | Criterio del límite |
|---|---|---|---|
| 🟢 Verde | (36, 50, 40) | (85, 255, 255) | Límite inf. ajustado para no captar verde-amarillento bajo luz cálida |
| 🟡 Amarillo | (20, 80, 80) | (35, 255, 255) | Ventana estrecha + S alta para excluir ocres y marrones |
| 🔴 Rojo — rango 1 | (0, 120, 70) | (10, 255, 255) | Límite inferior del círculo cromático |
| 🔴 Rojo — rango 2 | (170, 120, 70) | (179, 255, 255) | Límite superior — obligatorio unir ambas máscaras |

Estos valores son punto de partida. Las pruebas de la Parte 7 los van a ajustar según las condiciones reales del laboratorio.

### Diagrama de flujo

El diagrama debe reflejar estas etapas en orden, con bifurcaciones en la lógica de decisión:

1. Captura del frame
2. Preprocesado (resize + suavizado)
3. Conversión BGR → HSV
4. Generación de máscaras binarias por color
5. Filtrado morfológico
6. Conteo de píxeles activos por máscara
7. Lógica de decisión: ¿supera umbral? ¿es estable N frames? ¿cambió respecto al último envío?
8. Transmisión del comando
9. Actuación física (LED / tira WS2812B)

---

## Parte 2 — Entorno de trabajo

### Qué hay que producir

- Listado de dependencias con la función específica de cada una en este proyecto.
- Verificación de que el entorno funciona antes de avanzar: cámara accesible, puerto serial detectado.
- Para la extensión: Dockerfile configurado y validado.

### Dependencias y su rol

**Núcleo obligatorio:** `numpy`, `opencv-python`, `pyserial`

**Extensión avanzada:** `opencv-python-headless` (reemplaza al anterior en servidor sin GUI), `fastapi`, `uvicorn`, `paho-mqtt`

La distinción entre `opencv-python` y `opencv-python-headless` es una decisión de arquitectura que vale la pena documentar: la variante headless elimina las dependencias gráficas X11, necesarias para ejecutar en un servidor Linux sin entorno de escritorio.

### Criterio de avance

No continuar a la Parte 3 hasta tener confirmado: frame capturado, resolución visible, puerto serial detectado. Un script de verificación de entorno es el primer artefacto ejecutable del proyecto.

---

## Parte 3 — Detección de colores

### Qué hay que producir

- Módulo de detección independiente del medio de entrada (cámara local o WebSocket).
- Salidas visuales de cada etapa del pipeline — obligatorias para la defensa.

### Pipeline de procesamiento

El algoritmo debe estar estructurado como un pipeline de etapas discretas, no como un script monolítico. Cada etapa tiene entrada y salida definidas. Esto permite mostrar cada paso durante la defensa y facilita el ajuste de parámetros en Parte 7.

**Etapas y su propósito:**

| Etapa | Operación | Por qué |
|---|---|---|
| Preprocesado | Resize + GaussianBlur | Reducir carga de cómputo y eliminar ruido de alta frecuencia |
| Conversión | BGR → HSV | Aislar el matiz para segmentación robusta |
| Máscaras | `inRange` por rango | Segmentar cada color en binario |
| Suma rojo | `cv2.add` de dos máscaras | Capturar ambos extremos del espectro rojo |
| Morfología | Cierre morfológico | Rellenar huecos, unir fragmentos, limpiar contornos |
| Cuantificación | `countNonZero` | Obtener métrica de presencia por color |

### Visualización de etapas

Durante la defensa, el profe va a querer ver el proceso. Las ventanas a mostrar son: frame original, imagen HSV, máscara binaria por color, resultado de `bitwise_and` por color, y estado final con overlay de texto. Esto no es opcional si se quiere defender bien.

---

## Parte 4 — Comunicación y lógica de decisión

### Qué hay que producir

- Lógica de decisión con tres filtros anti-ruido en cadena.
- Módulo de comunicación serial para Arduino.
- Módulo MQTT para la extensión con ESP32.

### Los tres filtros anti-ruido (el profe los pide explícitamente)

El sistema no debe enviar un comando por cada frame — eso satura el canal y genera parpadeo en los LEDs. La lógica de envío aplica tres filtros en cadena:

1. **Umbral de píxeles:** si el conteo no supera un mínimo, la detección se descarta. Elimina reflejos y sombras pequeñas.
2. **Historial de frames:** el color debe mantenerse estable durante N frames consecutivos antes de confirmar. Elimina detecciones transitorias.
3. **Comparación con último envío:** solo se transmite si el color confirmado es distinto al último enviado. Evita saturar el canal con comandos redundantes.

Estos tres filtros son decisiones de diseño documentables con impacto medible en las pruebas.

### Protocolo de comunicación

**Serial (Arduino):** envío de un único carácter por detección confirmada: `R`, `G`, `Y`, `N`. Simple, robusto, sin overhead.

**MQTT (ESP32):** mismo esquema de caracteres, publicados en el tópico `utn/vision/tp2/color`. El broker Mosquitto corre localmente en el mismo servidor que el backend.

---

## Parte 5 — Sistema embebido

### Qué hay que producir

- Firmware Arduino con lógica `switch-case` y retroalimentación por monitor serial.
- Firmware ESP32 con suscripción MQTT y control de tira WS2812B (extensión).

### Criterios de diseño del firmware

**Arduino:** la lógica es simple por diseño — recibir un carácter, apagar todos los LEDs, encender el correspondiente. Lo importante es el manejo correcto del buffer serial y la retroalimentación por monitor serie para depuración.

**ESP32:** agrega reconexión automática ante pérdida de Wi-Fi o broker MQTT. Este es un criterio de calidad de implementación que el profe puede verificar desconectando el broker durante la demo.

### Esquema de conexión a documentar

El circuito Arduino con LEDs discretos y resistencias debe estar esquematizado en el informe. El esquema ESP32 + WS2812B debe incluir alimentación separada para la tira si el número de LEDs es alto.

---

## Parte 6 — Interfaz web (opcional → valor agregado directo)

### Qué aporta a la nota

Cubre el 10% de creatividad y genera el diferencial más visible en la defensa. No es decorativa — tiene función pedagógica concreta.

### Dos modos de operación

**Modo Directo:** video en vivo + resultado de detección. Simula el sistema en producción. Lo que el evaluador ve cuando demuestra que funciona.

**Modo Laboratorio:** sliders de rangos HSV en tiempo real, máscaras binarias visibles, conteo de píxeles por color. Permite demostrar dominio del algoritmo modificando parámetros en vivo ante el profe.

### El momento clave en la defensa

Activar el Modo Laboratorio, desplazar el límite superior de H del amarillo hacia el rango del verde, y mostrar en vivo cómo el sistema empieza a confundir colores. Luego corregirlo. Eso demuestra comprensión real del algoritmo — no solo que compila y corre.

---

## Parte 7 — Pruebas e integración

### Qué hay que producir

- Tabla de escenarios de prueba con condición, comportamiento esperado y resultado observado.
- Registro de ajustes de parámetros con justificación de cada cambio.
- Análisis de latencia del sistema completo.

### Escenarios obligatorios a documentar

| Escenario | Condición a reproducir | Qué observar |
|---|---|---|
| Óptimo | Luz difusa, fondo oscuro, objeto mate | Detección estable, sin parpadeo, tiempo de respuesta |
| Baja iluminación | Sombras parciales sobre el objeto | Comportamiento de V mínimo como filtro |
| Contraluz / reflejo | Luz directa hacia la cámara | Degradación de S — pérdida de firma espectral |
| Solapamiento | Luz cálida sobre objeto verde | Desplazamiento de H hacia rango amarillo |

### Parámetros a calibrar durante las pruebas

- Umbral mínimo de píxeles: balance entre sensibilidad y falsas detecciones.
- Cantidad de frames de estabilidad: balance entre velocidad de respuesta y estabilidad.
- Límites H del verde e H del amarillo: el ajuste crítico para evitar solapamiento.

Cada ajuste debe quedar documentado en el informe con el valor anterior, el valor nuevo y la razón del cambio.

---

## Estructura del informe final

```
1. Portada
2. Introducción — objetivo y alcance del proyecto
3. Marco Teórico
   3.1 Análisis estructural RGB vs HSV
   3.2 Rangos HSV: criterios de selección y ajuste
   3.3 Protocolos de comunicación utilizados
4. Diseño del Sistema
   4.1 Arquitectura por capas
   4.2 Diagrama de flujo del algoritmo
   4.3 Esquema de conexión hardware
5. Desarrollo por etapas
   5.1 Motor de detección
   5.2 Lógica de decisión anti-ruido
   5.3 Comunicación serial / MQTT
   5.4 Firmware embebido
   5.5 Interfaz web (si se implementa)
6. Pruebas y Resultados
   6.1 Tabla de escenarios con resultados
   6.2 Registro de ajuste de parámetros
   6.3 Análisis de latencia
7. Conclusiones — dificultades, aprendizaje, propuestas de mejora
8. Referencias
9. Anexos — código fuente comentado + enlace al video demostrativo
```

---

## Estructura del proyecto

```
tp2_vision/
├── python/          ← backend: detector, lógica, comunicación
├── arduino/         ← firmware Arduino
├── esp32/           ← firmware ESP32 (extensión)
├── docker/          ← Dockerfile y configuración (extensión)
├── web/             ← interfaz HTML/JS (extensión)
└── informe/         ← PDF final
```

---

## Entregables

- [ ] Código fuente comentado — Python y Arduino/ESP32
- [ ] Informe técnico en PDF
- [ ] Video demostrativo — máximo 5 minutos

**Estructura sugerida para el video:**
- 0:00–0:30 — Arquitectura del sistema en una imagen
- 0:30–2:00 — Demo funcional: tres colores, LEDs respondiendo
- 2:00–3:30 — Modo Laboratorio: máscaras, sliders, solapamiento en vivo
- 3:30–5:00 — Escenario de estrés: baja luz, contraluz, límites del sistema
