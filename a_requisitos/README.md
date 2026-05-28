# A_requisitos — Contrato y Alcance del Trabajo Práctico

## Objetivo de esta carpeta

La carpeta `a_requisitos/` contiene el material contractual y académico que define formalmente el alcance del Trabajo Práctico Nº2 de la materia Visión Artificial.

Esta sección representa el punto de partida del proyecto y establece:

- requerimientos obligatorios,
- objetivos funcionales,
- restricciones técnicas,
- criterios de evaluación,
- entregables,
- y lineamientos generales definidos por la cátedra.

---

# Contenido principal

## PDF oficial del TP

Archivo: `LA___Visión_Artifical___TP2.pdf`

Documento provisto por la cátedra que contiene:

- objetivos generales,
- descripción del procedimiento,
- partes del desarrollo,
- consignas obligatorias,
- requisitos mínimos,
- criterios de evaluación,
- y formato de entrega.

## Rol de esta carpeta dentro del proyecto

La carpeta `a_requisitos/` funciona como:

- referencia contractual,
- fuente oficial de requerimientos,
- base de validación técnica,
- y criterio de aceptación del sistema desarrollado.

Toda decisión de diseño e implementación realizada posteriormente debe mantener coherencia con los requerimientos definidos en esta etapa.

## Alcance funcional del TP

El sistema solicitado por la cátedra debe ser capaz de:

- Capturar imágenes en tiempo real.
- Detectar colores mediante visión artificial.
- Procesar información utilizando OpenCV.
- Determinar el color predominante.
- Comunicar resultados mediante puerto serial.
- Actuar físicamente mediante un microcontrolador.

## Tecnologías involucradas

### Procesamiento
- Python
- OpenCV
- NumPy

### Comunicación
- PySerial
- Comunicación serial USB

### Sistema embebido
- ESP32-S3
- LED WS2812B

## Componentes físicos utilizados

- **Cámara web:** Redragon HD 720P
- **Microcontrolador:** ESP32-S3 SuperMini
- **Actuación visual:** LED RGB direccionable WS2812B integrado

## Estructura general del trabajo

El TP se encuentra dividido en siete partes principales:

| Parte | Descripción |
| --- | --- |
| Parte 1 | Análisis y diseño |
| Parte 2 | Configuración del entorno |
| Parte 3 | Detección de colores |
| Parte 4 | Comunicación serial |
| Parte 5 | Programación embebida |
| Parte 6 | Integración y pruebas |
| Parte 7 | Mejoras opcionales |

## Criterios de evaluación

La evaluación contempla:

| Criterio | Peso |
| --- | --- |
| Funcionamiento técnico | 40% |
| Calidad de implementación | 30% |
| Documentación y análisis | 20% |
| Creatividad y mejoras | 10% |

## Objetivo metodológico

Esta carpeta no contiene desarrollo técnico ni implementación.

Su finalidad es:

- definir claramente el problema,
- comprender el alcance académico,
- y establecer el marco formal sobre el cual se construirá el prototipo.

## Relación con las demás carpetas

```text
a_requisitos/
    ↓
b_investigacion/
    ↓
c_prototipado/
    ↓
d_presentacion/
```

La información definida aquí será utilizada como referencia durante todas las etapas posteriores del proyecto.

## Resultado esperado

Al finalizar esta etapa debe existir:

- comprensión clara del problema,
- identificación de requerimientos,
- definición del alcance,
- y validación de los objetivos generales del TP.