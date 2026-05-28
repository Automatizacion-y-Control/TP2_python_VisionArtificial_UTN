# C_prototipado — Implementación y Desarrollo del Sistema

## Objetivo de esta carpeta

La carpeta `c_prototipado/` contiene el desarrollo práctico e implementación funcional del sistema de visión artificial solicitado en el Trabajo Práctico Nº2.

En esta etapa se construye el sistema completo:

- captura de imagen,
- procesamiento HSV,
- detección de colores,
- toma de decisiones,
- comunicación serial,
- y actuación mediante ESP32-S3 y LED WS2812B.

---

## Objetivo general del prototipado

Desarrollar un sistema capaz de:

1. Capturar video en tiempo real.
2. Detectar colores mediante OpenCV.
3. Determinar el color predominante.
4. Comunicar el resultado al microcontrolador.
5. Actuar físicamente mediante iluminación RGB.

---

## Contenido de la carpeta

```text
c_prototipado/
├── README.md
├── parte2_entorno/
├── parte3_deteccion/
├── parte4_comunicacion/
├── parte5_embebido/
├── parte6_integracion/
└── parte7_mejoras/
```

---

## Parte 2 — Configuración del entorno

### Objetivo

Preparar el entorno de desarrollo y validar la captura de video mediante OpenCV.

### Contenido esperado

#### Instalación de bibliotecas
```bash
pip install numpy opencv-python pyserial
```

#### Bibliotecas utilizadas

| Biblioteca | Función |
| --- | --- |
| `numpy` | Operaciones matriciales y procesamiento numérico |
| `opencv-python` | Visión artificial y procesamiento de imágenes |
| `pyserial` | Comunicación serial con ESP32-S3 |

### Resultados esperados

- Cámara funcional.
- Captura de video en tiempo real.
- Visualización de frames.
- Validación del entorno Python/OpenCV.

---

## Parte 3 — Detección de colores

### Objetivo

Implementar el sistema de segmentación HSV y detección de colores.

### Funcionalidades desarrolladas

#### Conversión de espacio de color
```python
cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
```

#### Máscaras binarias
Detección de:
- Rojo
- Verde
- Amarillo

#### Particularidad del rojo
El rojo utiliza dos rangos HSV independientes:
```python
cv2.add(mask_red1, mask_red2)
```

### Visualización requerida

El sistema debe mostrar:

- Imagen original.
- Imagen HSV.
- Máscaras binarias.
- Resultado de `bitwise_and`.
- Estado final de detección.

### Cuantificación de color

Conteo de píxeles activos mediante:
```python
cv2.countNonZero()
```

Implementación de umbral mínimo para evitar ruido.

---

## Parte 4 — Comunicación serial

### Objetivo

Transmitir el color detectado desde Python hacia el ESP32-S3.

### Funcionalidades implementadas

#### Comunicación serial
```python
serial.Serial()
```

#### Algoritmo de decisión
El sistema debe:

- determinar color predominante,
- evitar falsas detecciones,
- reducir ruido,
- evitar reenvíos innecesarios.

### Estrategias anti-ruido

#### Umbral mínimo de píxeles
Evita detecciones pequeñas o reflejos.

#### Contador de estabilidad
El color debe mantenerse estable durante varios frames consecutivos.

#### Comparación con último color enviado
Evita saturar la comunicación serial.

### Comandos enviados

| Color | Comando |
| --- | --- |
| Rojo | `R` |
| Verde | `G` |
| Amarillo | `Y` |
| Ninguno | `N` |

---

## Parte 5 — Sistema embebido

### Objetivo

Controlar el LED WS2812B mediante ESP32-S3.

### Hardware utilizado

- **ESP32-S3 SuperMini**
  <br><img src="./img/esp32s3_supermini.png" width="250">
- **LED WS2812B integrado**
  <br><img src="./img/ws2812b.png" width="180">

### Funcionalidades implementadas

- Inicialización serial.
- Recepción de comandos.
- Interpretación mediante `switch-case`.
- Control RGB del LED.
- Retroalimentación por monitor serial.

### Comportamiento esperado

| Comando | Acción |
| --- | --- |
| `R` | LED rojo |
| `G` | LED verde |
| `Y` | LED amarillo |
| `N` | LED apagado |

---

## Parte 6 — Integración y pruebas

### Objetivo

Validar el funcionamiento completo del sistema.

### Escenarios de prueba

- **Iluminación normal:** Funcionamiento esperado estable.
- **Baja iluminación:** Evaluar impacto sobre canal Value.
- **Contraluz y reflejos:** Evaluar ruido y falsas detecciones.
- **Solapamiento cromático:** Especialmente amarillo ↔ verde.

### Actividades realizadas

- Ajuste de rangos HSV.
- Inserción de mensajes de depuración.
- Validación de estabilidad.
- Medición de comportamiento.

---

## Parte 7 — Mejoras y desafíos adicionales

### Objetivo

Agregar funcionalidades opcionales para mejorar robustez y presentación del sistema.

### Mejoras implementables

#### Filtrado y morfología
- Gaussian Blur
- Erode
- Dilate
- Morphological Closing

#### Rangos adaptativos HSV
Ajuste dinámico según iluminación.

#### Detección de formas
Posibilidad de identificar:
- círculos,
- cuadrados,
- objetos específicos.

#### Interfaz gráfica
Posible implementación de:
- trackbars HSV,
- histogramas,
- visualización avanzada,
- calibración en tiempo real.

---

## Resultado esperado del prototipado

Al finalizar esta etapa el sistema debe:

- detectar colores en tiempo real,
- comunicarse correctamente con ESP32-S3,
- controlar el LED WS2812B,
- y responder de forma estable bajo diferentes condiciones de prueba.

---

## Relación con el informe final

Todo el material desarrollado en esta carpeta será utilizado posteriormente en:

- informe técnico,
- documentación del algoritmo,
- análisis de resultados,
- y defensa oral del proyecto.