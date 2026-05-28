# Protocolo de Comunicacion Serial - TP2

Este documento detalla el protocolo de comunicacion serial entre el proceso del host
(deteccion/vision) y el microcontrolador ESP32-C3 (control embebido) para el control
de uno o varios LEDs WS2812B externos.

La parte de deteccion pertenece al host. El firmware no asume como se obtiene esa
informacion: solamente recibe bytes por serie, los valida y actualiza la salida LED.

---

## 1. Parametros de Configuracion del Puerto Serial

Ambos extremos deben estar configurados con los mismos parametros fisicos para evitar
la corrupcion de datos:

| Parametro | Valor por defecto | Notas |
| :--- | :--- | :--- |
| **Baud Rate (Velocidad)** | `115200` bps | Velocidad estable y suficiente para comandos de texto. |
| **Data Bits** | `8` | Tamano estandar de palabra. |
| **Parity (Paridad)** | `None` | Sin bit de paridad. |
| **Stop Bits** | `1` | Bit de parada estandar. |
| **Flow Control** | `None` | Sin control de flujo de hardware o software. |
| **Codificacion** | ASCII | Comandos de texto. |

---

## 2. Fase 1: Protocolo de Caracter Unico (Base)

Es el protocolo inicial para validar el funcionamiento y cumplir con el alcance minimo
obligatorio del trabajo practico.

### Descripcion del Flujo

El host procesa su entrada, determina un estado de color y transmite un unico caracter
ASCII cuando corresponde actualizar la salida. El microcontrolador interpreta ese
caracter y aplica el color global a la salida WS2812B.

### Comandos Transmitidos

| Caracter ASCII | Byte (Hex) | Color Destino | Comportamiento de la salida WS2812B |
| :---: | :---: | :--- | :--- |
| **`R`** | `0x52` | Rojo | Encender en rojo puro `RGB(255, 0, 0)`. |
| **`G`** | `0x47` | Verde | Encender en verde puro `RGB(0, 255, 0)`. |
| **`Y`** | `0x59` | Amarillo | Encender en amarillo `RGB(255, 200, 0)`. |
| **`N`** | `0x4E` | Ninguno | Apagar `RGB(0, 0, 0)`. |

Formato recomendado:

```text
R\n
G\n
Y\n
N\n
```

El firmware tambien puede aceptar el caracter aislado (`R`, `G`, `Y`, `N`) si llega
sin salto de linea, pero se recomienda terminar los comandos con `\n`.

---

## 3. Fase 2: Protocolo de Trama Dinamica (Mejora)

Una vez validada la Fase 1, se puede usar una trama de texto para controlar valores
RGB, brillo o LEDs individuales.

### Estructura General de Trama

```text
<COMANDO,param1,param2,...>\n
```

Reglas:

- **`<`**: delimitador de inicio de trama.
- **`>`**: delimitador de fin de trama.
- **`\n`**: salto de linea recomendado para cierre de mensaje.
- Los parametros numericos se transmiten como enteros ASCII.
- Los valores RGB y brillo validos son `0..255`.
- Los indices de LED validos son `0..WS2812_LED_COUNT-1`.
- Una trama invalida se ignora y no modifica el estado actual.

### Color Global

```text
<A,r,g,b>\n
```

Aplica el mismo color a todos los LEDs.

Ejemplos:

```text
<A,255,0,0>
<A,0,255,0>
<A,255,200,0>
<A,0,0,0>
```

### Pixel Individual

```text
<P,index,r,g,b>\n
```

Actualiza un solo LED de la tira.

Ejemplo:

```text
<P,3,255,0,0>
```

Enciende el LED de indice `3` en rojo.

### Brillo Global

```text
<B,value>\n
```

Configura el brillo global usado por el firmware.

Ejemplos:

```text
<B,32>
<B,128>
<B,255>
```

### Apagado

```text
<OFF>\n
```

Apaga todos los LEDs. Es equivalente a `N\n` o `<A,0,0,0>\n`.

---

## 4. Parte del Firmware ESP32-C3

Esta es la parte que implementa el microcontrolador. No define como trabaja el host;
solo define que acepta el firmware y que hace con esos datos.

### Hardware de Salida

El ESP32-C3 maneja una salida WS2812B externa mediante un GPIO configurado en el
firmware.

Valores a definir en el codigo:

```c
#define WS2812_GPIO GPIO_NUM_X
#define WS2812_LED_COUNT N
```

`GPIO_NUM_X` debe reemplazarse por el pin fisico usado como linea de datos de la tira.
`N` es la cantidad de LEDs direccionables.

El LED onboard comun del ESP32-C3 no se usa para color RGB ni para WS2812B.

### Comportamiento del Receptor

El firmware debe:

- Leer el puerto serie sin bloquear la tarea principal.
- Parsear byte por byte con una maquina de estados.
- Limitar el tamano maximo de trama para evitar overflow.
- Validar cantidad de parametros, rangos RGB e indices.
- Ignorar comandos desconocidos.
- Mantener el ultimo estado valido si llega basura serial.
- Actualizar la tira solo cuando recibe un comando valido.

Timeout recomendado:

```text
Si no llega ningun comando valido durante 2000 ms, apagar la tira.
```

Esto evita que los LEDs queden encendidos indefinidamente si se corta la comunicacion.

### Respuestas del ESP32-C3

Para mantener el protocolo simple, el firmware puede funcionar sin respuestas.

Si se habilitan respuestas, usar texto corto:

| Respuesta | Significado |
| :--- | :--- |
| `OK\n` | Comando aplicado |
| `ERR\n` | Comando recibido pero invalido |

Si el host no lee respuestas, conviene desactivarlas y dejar solo logs locales de
depuracion.

### Compatibilidad Minima del Firmware

La implementacion inicial del firmware debe soportar como minimo:

```text
R\n
G\n
Y\n
N\n
```

La implementacion completa debe soportar:

```text
R\n
G\n
Y\n
N\n
<A,r,g,b>\n
<P,index,r,g,b>\n
<B,value>\n
<OFF>\n
```

---

## 5. Pruebas y Monitoreo del Puerto Serial

Dado que el protocolo se basa en caracteres de texto estandar, se puede probar el
microcontrolador de forma aislada desde un monitor serie:

1. Configurar el monitor a `115200` baud, `8N1`, sin control de flujo.
2. Para Fase 1, enviar `R`, `G`, `Y` o `N`.
3. Para Fase 2, enviar por ejemplo `<A,255,0,0>` o `<P,0,0,255,0>`.

Cuando otro proceso tenga abierto el puerto serie, el monitor tradicional no podra
abrirlo al mismo tiempo.
