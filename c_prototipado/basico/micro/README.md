# Módulo de Microcontrolador — Control Embebido (TP2)

Este directorio está destinado a almacenar el firmware desarrollado para el microcontrolador **ESP32-C3** encargado de actuar sobre el LED RGB direccionable WS2812B en función de los comandos enviados por el host Python.

---

## 1. Especificaciones de Implementación Requeridas

El firmware del microcontrolador debe estructurarse para cumplir con las siguientes consignas y particularidades de la integración:

### Configuración del Hardware
* **LED WS2812B:** Debe definirse el GPIO físico al cual está conectada la línea de datos de la tira y la cantidad de píxeles activos (ej: 1 LED onboard o tira externa).
* **Parámetros del Puerto Serie:** Configurado a **`115200 bps`**, 8 bits de datos, sin paridad y 1 bit de parada (`8N1`).

### Lógica del Firmware (Máquina de Estados)
1. **Lectura No Bloqueante:** El firmware debe leer del puerto serie byte por byte de manera asíncrona (evitando retardos bloqueantes como `delay()`) para garantizar que la respuesta del LED sea inmediata.
2. **Soporte de Fase 1 (Base):**
   * Debe parsear los comandos de carácter único terminados en salto de línea: `R\n`, `G\n`, `Y\n`, `N\n`.
   * Mapear cada carácter a su correspondiente valor de color en el LED WS2812B.
3. **Soporte de Fase 2 (Mejora):**
   * Debe identificar tramas delimitadas por `<` e inicio de comando `A` para color global, parseando los valores R, G, B separados por comas y finalizados en `>\n` (ej: `<A,255,128,0>\n`).
4. **Filtro de Inactividad (Timeout de Seguridad):**
   * Si no se recibe ningún comando serie válido durante **2000 ms**, el microcontrolador debe apagar automáticamente la tira LED (`RGB(0,0,0)`). Esto previene que el LED quede encendido de manera indefinida si se cuelga la aplicación de visión artificial en el host o se desconecta el cable.

---

## 2. Documentación Relacionada

Para consultar ejemplos de código en C++ (estilo Arduino/ESP-IDF) con parseadores de tramas no bloqueantes utilizando tokens y máquinas de estado, revisá el archivo:
* **[protocoloSerie.md](file:///d:/UTN/Licenciaturas/Automatizacion%20y%20Control/Nivel%202/1er%20Cuatrimestre/7%20Introduccion%20a%20la%20vision%20artificial/3%20Entregas/TP2/c_prototipado/basico/python/protocoloSerie.md)** (ubicado en la carpeta hermana de Python).
