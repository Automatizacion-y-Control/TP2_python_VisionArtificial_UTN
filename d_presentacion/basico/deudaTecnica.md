# Registro de Deuda Técnica — TP2 Desktop Dashboard

Este documento registra los atajos, simplificaciones y compromisos de diseño asumidos durante el desarrollo de la aplicación PyQt5, junto con su plan de mitigación.

---

## 1. Deudas Técnicas Identificadas

### A. Simulación Serial (Mock Mode)
* **Descripción:** Si no hay un microcontrolador conectado al puerto USB, la aplicación simula la salida por consola para no bloquear la ejecución.
* **Impacto:** Permite probar el software de visión, pero no garantiza el comportamiento de la comunicación serie física hasta que se conecte el hardware.
* **Mitigación:** Realizar pruebas periódicas con la placa ESP32-C3 y el firmware cargado en Fase 1 y Fase 2.

### B. Índice de Cámara Web Fijo
* **Descripción:** Por defecto, el capturador de video utiliza el índice `0`.
* **Impacto:** Si el usuario tiene múltiples cámaras conectadas (por ejemplo, una cámara integrada y una webcam externa Redragon), podría abrir el sensor incorrecto.
* **Mitigación:** Se debe agregar un combobox en la interfaz para permitir que el operador elija el índice de la cámara (`0, 1, 2, ...`) dinámicamente.

### C. Calibración en Formato JSON Local
* **Descripción:** Los perfiles de calibración se guardan de forma local en la carpeta de ejecución del script en un archivo de texto plano `.json`.
* **Impacto:** Los datos son legibles y fáciles de alterar manualmente, pero carecen de validación de integridad o encriptación.
* **Mitigación:** Validar los rangos leídos al iniciar la aplicación para asegurar que H esté en `0..179` y S/V en `0..255`.

### D. Frecuencia de Actualización del Hilo de Cámara (QThread)
* **Descripción:** El procesamiento de imágenes corre en un hilo secundario para evitar congelar la interfaz de Qt. La sincronización se realiza mediante señales de Qt (`pyqtSignal(QImage)`).
* **Impacto:** A altas resoluciones, el envío continuo de imágenes grandes por el sistema de señales puede elevar el uso de CPU.
* **Mitigación:** Redimensionar el frame procesado a `640x480` antes de convertirlo a formato `QImage` para el dibujado en el widget.

---

## 2. Plan de Refactorización y Mitigación

| ID Deuda | Gravedad | Sprint de Resolución | Acción a Tomar |
| :--- | :---: | :---: | :--- |
| **A (Serial Mock)** | Baja | Sprint 1 / Constante | Logs claros en pantalla indicando si los datos son simulados o físicos. |
| **B (Selección de Cámara)** | Media | Sprint 2 | Añadir selector dinámico de cámaras en el panel de herramientas. |
| **C (Validación de JSON)** | Baja | Sprint 3 | Bloque try-except con validación de tipos al cargar el archivo de configuración. |
| **D (Rendimiento QThread)** | Media | Sprint 2 | Procesar frames en baja resolución para la visualización en la app. |
