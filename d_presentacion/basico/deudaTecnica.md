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

### E. Tamaño de Fuente de la Interfaz
* **Descripción:** El tamaño de fuente base de los widgets (labels, botones, sliders) fue fijado en 12px durante el diseño inicial sin ajuste fino sobre hardware real.
* **Impacto:** En pantallas de escritorio con resolución estándar (1080p) la interfaz puede resultar de lectura incómoda, especialmente en la terminal de log y el calibrador HSV.
* **Mitigación:** Incrementar progresivamente en pasos de 0.5–1 punto (12 → 12.5 → 13...) el tamaño de fuente base en `styles.py` hasta que el usuario valide la legibilidad. Mantener coherencia entre los distintos componentes (header, grupos, terminal, badges).

### F. Distribución de la Vista de Máscaras
* **Descripción:** La pestaña "MÁSCARAS" divide la pantalla en 3 paneles horizontales iguales (213px cada uno), lo que deja poco espacio de detalle por color y no aprovecha el área sobrante para información contextual.
* **Impacto:** Las máscaras se ven pequeñas y no hay espacio para mostrar datos adicionales (umbral activo, píxeles en tiempo real, estado del filtro) junto a cada máscara.
* **Mitigación:** Rediseñar la vista de máscaras exclusivamente en `camera_thread.py` (`_build_masks_panel`) y el QLabel de destino: dividir el área en **4 cuadrantes** (2×2) — los 3 superiores para cada color (más grandes) y el cuadrante inferior derecho para un panel de métricas con pixeles activos, umbral configurado y estado de detección.

### G. Modo de Comportamiento de la Salida LED (Persistencia vs. Pulso)
* **Descripción:** El comportamiento actual de la actuación LED es de tipo "pulso": al detectar un color se envía el comando y el LED se apaga luego de un tiempo `t` definido por el timeout del firmware del ESP32 (~2 segundos). No hay forma de elegir el modo desde la UI.
* **Impacto:** Para ciertos casos de uso es deseable que el LED **siga la detección en tiempo real** (se mantiene encendido mientras el color persiste, y se apaga inmediatamente al detectar "NINGUNO"), en lugar de pulsos de duración fija.
* **Mitigación:** Agregar un selector de modo en el panel izquierdo ("Modo LED"): `Pulso (timeout firmware)` vs. `Continuo (sigue detección)`. En modo continuo, el heartbeat del `QTimer` de 1 segundo enviaría el color confirmado activo en cada tick, manteniendo el LED activo mientras la detección persista.

### I. Tema Claro — Dark/Light Toggle (Luna/Sol)
* **Descripción:** La aplicación solo cuenta con el tema oscuro industrial definido en `styles.py` (`DARK_QSS`). No existe un tema claro alternativo ni un mecanismo para switchear entre ambos en tiempo de ejecución.
* **Impacto:** En entornos con buena iluminación ambiente (laboratorio con luz natural, proyector) el tema oscuro puede dificultar la lectura. Un tema claro tipo panel de control diurno mejora la usabilidad en esos contextos.
* **Referencia de paleta:** La paleta del modo claro debe inspirarse en la interfaz del Antigravity IDE (fondo blanco/gris muy claro, texto oscuro, acento azul profesional), manteniendo la misma estructura de layout y componentes — solo cambia la hoja de estilos QSS aplicada.
* **Mitigación:** Definir `LIGHT_QSS` en `styles.py` con paleta clara (fondo `#F0F2F5`, paneles `#FFFFFF`, acento `#0078D4`, texto `#1E1E2E`). Agregar en el header de `main_window.py` un `QPushButton` con icono 🌙/☀️ que llame a `app.setStyleSheet()` en el toggle. El estado del tema debe persistir en `calibration.json`.

### H. Proporciones y Armonía Visual del Layout (Header, Asides, Footer)
* **Descripción:** El header, los paneles laterales (izquierdo y derecho) y la barra de log inferior tienen alturas y márgenes que no fueron ajustados con referencia a contenido real. Con la app corriendo se observan espacios no aprovechados y proporciones que pueden mejorarse.
* **Impacto:** La interfaz funciona correctamente pero no tiene la armonía visual de un panel industrial de referencia. Los márgenes del header son generosos en relación al resto, y el footer de log podría ganar altura o el header reducirse levemente.
* **Mitigación:** Revisar y ajustar en `main_window.py`: altura del header (56px → evaluar 50px), altura del log terminal (108px → evaluar 120px para mejor legibilidad), y márgenes internos de los `QGroupBox` laterales para lograr un ritmo visual consistente entre todas las secciones.

---

## 2. Plan de Refactorización y Mitigación

| ID Deuda | Gravedad | Prioridad | Acción a Tomar |
| :--- | :---: | :---: | :--- |
| **A (Serial Mock)** | Baja | Baja | Logs claros en pantalla indicando si los datos son simulados o físicos. |
| **B (Selección de Cámara)** | Media | ✅ Resuelta | Combobox dinámico implementado desde Sprint 1. |
| **C (Validación de JSON)** | Baja | Baja | Bloque try-except con validación de tipos implementado en `config.py`. |
| **D (Rendimiento QThread)** | Media | ✅ Resuelta | Frames redimensionados a 640×480 antes de conversión a QImage. |
| **E (Tamaño de Fuente)** | Baja | Media | Incrementar en pasos de 0.5–1pt en `styles.py` hasta validación del usuario. |
| **F (Vista de Máscaras 4 cuadrantes)** | Media | ✅ Resuelta | Panel 2×2 (640×480): 3 cuadrantes de máscara + cuadrante de métricas (px, umbral, estabilidad, color estable). |
| **G (Modo LED Pulso vs. Continuo)** | Media | ✅ Resuelta | Grupo "MODO LED" en panel izquierdo con botones ⚡ PULSO / ◎ CONTINUO. Heartbeat reenvía color activo cada 1s en modo continuo. |
| **H (Armonía Visual Layout)** | Baja | Media | Ajuste fino de alturas y márgenes en `main_window.py` y `styles.py`. |
| **I (Tema Claro / Dark-Light Toggle)** | Baja | Media | Agregar botón luna/sol en el header; definir `LIGHT_QSS` en `styles.py` con paleta clara. |
