# Protocolo de Comunicación Serial — TP2

Este documento detalla el protocolo de comunicación serial entre el script de Python (Visión Artificial) y el microcontrolador ESP32-S3 (Control Embebido) para el control del LED direccionable WS2812B.

---

## 1. Parámetros de Configuración del Puerto Serial

Ambos dispositivos deben estar configurados exactamente con los mismos parámetros físicos para evitar la corrupción de datos:

| Parámetro | Valor por defecto | Notas |
| :--- | :--- | :--- |
| **Baud Rate (Velocidad)** | `115200` bps | Velocidad óptima para microcontroladores modernos. |
| **Data Bits** | `8` | Tamaño estándar de palabra. |
| **Parity (Paridad)** | `None` (Ninguna) | Sin bit de paridad. |
| **Stop Bits** | `1` | Bit de parada estándar. |
| **Flow Control** | `None` | Sin control de flujo de hardware o software. |

---

## 2. Fase 1: Protocolo de Carácter Único (Base)

Es el protocolo inicial para validar el funcionamiento y cumplir con el alcance mínimo obligatorio del trabajo práctico.

### Descripción del Flujo
El script de Python procesa el video, aplica los filtros de estabilidad y, cuando determina un cambio en el color predominante, transmite **un único carácter ASCII**.

### Comandos Transmitidos

| Carácter ASCII | Byte (Hex) | Color Destino | Comportamiento del LED WS2812B |
| :---: | :---: | :--- | :--- |
| **`R`** | `0x52` | Rojo | Encender en Rojo puro `RGB(255, 0, 0)`. |
| **`G`** | `0x47` | Verde | Encender en Verde puro `RGB(0, 255, 0)`. |
| **`Y`** | `0x59` | Amarillo | Encender en Amarillo puro `RGB(255, 200, 0)`. |
| **`N`** | `0x4E` | Ninguno | Apagar el LED `RGB(0, 0, 0)`. |

### Estructura de Recepción en el ESP32 (Pseudo-C++)

El microcontrolador debe leer del puerto serie de forma no bloqueante y ejecutar la actuación mediante un `switch-case`:

```cpp
// Ejemplo de estructura de recepción básica en ESP32
#include <Adafruit_NeoPixel.h>

#define PIN_LED      48   // Pin GPIO del WS2812B integrado en ESP32-S3 SuperMini
#define NUMPIXELS    1

Adafruit_NeoPixel pixels(NUMPIXELS, PIN_LED, NEO_GRB + NEO_KHZ800);

void setup() {
  Serial.begin(115200);
  pixels.begin();
  pixels.clear();
  pixels.show();
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    
    switch (cmd) {
      case 'R':
        pixels.setPixelColor(0, pixels.Color(255, 0, 0));
        break;
      case 'G':
        pixels.setPixelColor(0, pixels.Color(0, 255, 0));
        break;
      case 'Y':
        pixels.setPixelColor(0, pixels.Color(255, 200, 0));
        break;
      case 'N':
        pixels.clear();
        break;
      default:
        // Carácter desconocido, no actuar
        break;
    }
    pixels.show();
  }
}
```

---

## 3. Fase 2: Protocolo de Trama Dinámica (Mejora)

Una vez validada la Fase 1, se puede implementar la Fase 2 como valor agregado para controlar directamente la mezcla de color RGB desde los sliders de Python en el LED físico.

### Estructura de la Trama
Para evitar el desfasaje de bytes en el búfer serial, los datos se envían en una trama de texto delimitada por caracteres de inicio y fin, con valores numéricos separados por comas:

$$\text{Trama: } \mathbf{<}\text{R}\mathbf{,}\text{G}\mathbf{,}\text{B}\mathbf{>}\backslash\text{n}$$

* **`<`** (ASCII `0x3C`): Delimitador de inicio de trama.
* **`R,G,B`**: Tres enteros representados como texto en formato ASCII (rango `0` a `255`).
* **`>`** (ASCII `0x3E`): Delimitador de fin de trama.
* **`\n`** (ASCII `0x0A`): Salto de línea para sincronización y fin de mensaje.

*Ejemplo:* Para enviar un naranja brillante `RGB(255, 128, 0)`, Python transmitirá la cadena `"<255,128,0>\n"`.

### Algoritmo de Parseo en el ESP32

Para recibir tramas dinámicas sin bloquear el microcontrolador, se recomienda usar una máquina de estados para leer los bytes uno a uno:

```cpp
// Ejemplo de parseo no bloqueante en ESP32
void readSerialFrame() {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;
  const byte numChars = 32;
  static char receivedChars[numChars];

  while (Serial.available() > 0) {
    rc = Serial.read();

    if (recvInProgress == true) {
      if (rc != endMarker) {
        if (ndx < numChars - 1) {
          receivedChars[ndx] = rc;
          ndx++;
        }
      } else {
        receivedChars[ndx] = '\0'; // Finalizar cadena
        recvInProgress = false;
        ndx = 0;
        parseAndAct(receivedChars);
      }
    } else if (rc == startMarker) {
      recvInProgress = true;
    }
  }
}

void parseAndAct(char* tempChars) {
  // Parsear tramas como "255,128,0"
  char* strtokIndx;
  
  strtokIndx = strtok(tempChars, ",");
  int r = atoi(strtokIndx);
  
  strtokIndx = strtok(NULL, ",");
  int g = atoi(strtokIndx);
  
  strtokIndx = strtok(NULL, ",");
  int b = atoi(strtokIndx);

  // Escribir en el WS2812B
  pixels.setPixelColor(0, pixels.Color(r, g, b));
  pixels.show();
}
```

---

## 4. Pruebas y Monitoreo del Puerto Serial

Dado que el protocolo se basa en caracteres de texto estándar, podés probar el microcontrolador de forma aislada sin usar Python:

1. **Usar el Monitor Serie de Arduino IDE / VSCode:**
   * Configura la velocidad del monitor a `115200`.
   * Para la **Fase 1**, escribe `R`, `G`, `Y` o `N` en la consola de entrada y presiona Enviar. El LED debe responder inmediatamente.
   * Para la **Fase 2**, escribe `<255,0,0>` o `<0,255,0>` y presiona Enviar.
2. **Monitoreo desde Python:**
   * Cuando el script de Python tome el control del puerto serie, no podrás abrir el Monitor Serie tradicional (ya que el puerto estará ocupado).
   * Por eso, el script de Python implementará logs en consola para mostrar exactamente qué bytes está inyectando en el bus.
