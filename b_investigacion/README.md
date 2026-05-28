# B_investigacion — Parte 1: Análisis y Diseño Básico

## Objetivo de esta carpeta

Esta carpeta contiene la investigación teórica y el diseño conceptual inicial correspondiente a la **Parte 1** del Trabajo Práctico Nº2 de Visión Artificial.

El objetivo principal es comprender los fundamentos de segmentación por color utilizando el espacio HSV y definir la arquitectura básica del sistema de detección y actuación mediante microcontrolador.

---

# Contenido

## 1. [Analisis_RGB_vs_HSV.md](./Analisis_RGB_vs_HSV.md)

Documento teórico que desarrolla:

- Diferencias entre los espacios de color RGB y HSV.
- Funcionamiento estructural de cada modelo.
- Problemas de RGB para segmentación por color.
- Ventajas de HSV para detección robusta.
- Justificación técnica de la elección de HSV en sistemas de visión artificial.

---

## 2. [Rangos_HSV.md](./Rangos_HSV.md)

Documento de calibración inicial de colores.

Incluye:

- Rangos HSV para:
  - Rojo
  - Verde
  - Amarillo
- Explicación del doble rango del color rojo.
- Influencia de la iluminación sobre:
  - Hue (Matiz)
  - Saturation (Saturación)
  - Value (Brillo)
- Consideraciones para ajuste experimental durante las pruebas.

---

## 3. [Diagrama_Flujo_Sistema.md](./Diagrama_Flujo_Sistema.md)

Diseño lógico básico del sistema.

El diagrama de flujo representa:

1. Captura de imagen.
2. Conversión de color y procesamiento.
3. Generación de máscaras binarias.
4. Detección y conteo de píxeles.
5. Toma de decisiones.
6. Comunicación serial/MQTT.
7. Actuación del microcontrolador.
8. Respuesta visual mediante LEDs.

---

## Objetivo técnico de la etapa

La Parte 1 busca definir:

- la lógica general del sistema,
- la estrategia de segmentación,
- y los parámetros iniciales de funcionamiento,

antes de comenzar la implementación práctica en Python y ESP32.

---

## Relación con el resto del proyecto

La información desarrollada en esta carpeta será utilizada posteriormente en:

- procesamiento de imágenes con OpenCV,
- definición de máscaras HSV,
- lógica de decisión,
- comunicación con ESP32,
- e informe técnico final.

---

## Estructura sugerida

```text
b_investigacion/
├── README.md
├── Analisis_RGB_vs_HSV.md
├── Rangos_HSV.md
└── Diagrama_Flujo_Sistema.md
```