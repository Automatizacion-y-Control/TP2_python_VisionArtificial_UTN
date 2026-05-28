# Plan de Implementación — Módulo de Detección en Python (TP2)

Este plan describe el diseño arquitectónico de la aplicación Python para captura de video, procesamiento de color HSV, filtrado anti-ruido y transmisión serial.

## User Review Required

> [!IMPORTANT]
> **Diseño Modular vs. Monolítico:** Se propone separar las responsabilidades en módulos independientes (configuración, detección, filtrado, comunicación y bucle principal) para cumplir con el criterio del 30% de "Calidad de implementación" de la cátedra y permitir una defensa técnica sólida.
> **Simulación Serial:** Dado que el microcontrolador no está conectado físicamente a esta máquina virtual, se implementará un modo de simulación o "Mock" para la comunicación serial para poder validar todo el flujo de Python sin fallas de conexión.

## Open Questions

> [!NOTE]
> 1. **Puerto Serial por Defecto:** ¿Tenés alguna preferencia de puerto serie (`COM3`, `/dev/ttyUSB0`, etc.) o preferís que implementemos una auto-detección del puerto COM activo?
> 2. **Configuración de Filtro Temporal:** El número por defecto de estabilidad temporal propuesto es de 5 frames. ¿Te parece adecuado o preferís parametrizarlo para ser modificable?

## Proposed Changes

Se propone crear el módulo de Python dentro de `c_prototipado/basico/python/` con la siguiente estructura limpia:

```text
c_prototipado/basico/python/
├── config.py         # Rangos HSV, umbrales y puertos de comunicación
├── detector.py       # Algoritmo de detección, conversión y generación de máscaras
├── filters.py        # Filtro de estabilidad temporal y descarte de ruido
├── serial_comm.py    # Control de conexión física serial con opción Mock
└── main.py           # Bucle principal de captura y visualización de OpenCV
```

---

### Python Prototyping Component

#### [NEW] [config.py](file:///d:/UTN/Licenciaturas/Automatizacion%20y%20Control/Nivel%202/1er%20Cuatrimestre/7%20Introduccion%20a%20la%20vision%20artificial/3%20Entregas/TP2/c_prototipado/basico/python/config.py)
* Almacenará los diccionarios de rangos HSV (verde, amarillo y las dos máscaras del rojo) definidos en la investigación previa.
* Contendrá los valores de configuración serial (Baudrate por defecto a 115200 o 9600) y de filtros (umbrales mínimos de píxeles activos y cantidad de frames estables `N`).

#### [NEW] [detector.py](file:///d:/UTN/Licenciaturas/Automatizacion%20y%20Control/Nivel%202/1er%20Cuatrimestre/7%20Introduccion%20a%20la%20vision%20artificial/3%20Entregas/TP2/c_prototipado/basico/python/detector.py)
* Definirá la clase `ColorDetector`.
* Método para preprocesar el frame (reducción de tamaño opcional + suavizado Gaussiano para quitar ruido).
* Método de generación de máscaras con `cv2.inRange`.
* Fusión del color rojo con `cv2.add`.
* Aplicación de operaciones morfológicas opcionales (apertura y cierre morfológico).
* Conteo de píxeles activos usando `cv2.countNonZero` y retorno de resultados en formato estructurado.

#### [NEW] [filters.py](file:///d:/UTN/Licenciaturas/Automatizacion%20y%20Control/Nivel%202/1er%20Cuatrimestre/7%20Introduccion%20a%20la%20vision%20artificial/3%20Entregas/TP2/c_prototipado/basico/python/filters.py)
* Definirá la clase `AntiNoiseFilter` para encapsular la lógica de estabilidad.
* **Filtro 1:** Descarte si el conteo de píxeles no supera el umbral configurado.
* **Filtro 2 (Estabilidad temporal):** Lleva un historial circular de los últimos `N` frames. Si el mismo color no se mantiene en los `N` frames de forma continua, no se confirma el cambio de estado.
* **Filtro 3 (Envío diferencial):** Solo retorna verdadero/emite señal si el color estable actual es distinto al último enviado.

#### [NEW] [serial_comm.py](file:///d:/UTN/Licenciaturas/Automatizacion%20y%20Control/Nivel%202/1er%20Cuatrimestre/7%20Introduccion%20a%20la%20vision%20artificial/3%20Entregas/TP2/c_prototipado/basico/python/serial_comm.py)
* Definirá la clase `SerialCommunicator`.
* Encapsulará a `serial.Serial`.
* Tendrá un fallback automático en modo simulación (si el puerto físico no responde o no está conectado) que imprimirá un log elegante de los datos virtuales enviados al microcontrolador.

#### [NEW] [main.py](file:///d:/UTN/Licenciaturas/Automatizacion%20y%20Control/Nivel%202/1er%20Cuatrimestre/7%20Introduccion%20a%20la%20vision%20artificial/3%20Entregas/TP2/c_prototipado/basico/python/main.py)
* Instanciará el pipeline completo.
* Bucle principal capturando frames con `cv2.VideoCapture`.
* Inserción de textos en pantalla (overlays con color predominante, FPS, cantidad de píxeles).
* Creación de ventanas auxiliares para control en vivo (Original, HSV, Máscaras binarias, bitwise_and).

---

## Verification Plan

### Automated Tests
* Ejecución de pruebas manuales y simulación ejecutando:
  ```powershell
  python c_prototipado/basico/python/main.py --simulate
  ```
  Esto validará el ciclo completo de captura de video de la webcam (o lectura de un video de prueba), procesamiento HSV, filtrado anti-ruido, visualización gráfica y simulación serial en consola.

### Manual Verification
* Conexión física del ESP32-S3 e indicación visual. El usuario podrá probar la conexión seleccionando el puerto COM correcto (ej. `COM5`) y verificando el LED físico.
