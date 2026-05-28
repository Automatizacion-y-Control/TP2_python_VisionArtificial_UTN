# Planificación Ágil — SCRUM (TP2 Desktop Dashboard)

Este documento define el marco de trabajo SCRUM para la implementación de la aplicación de escritorio avanzada de visión artificial y control en PyQt5.

---

## 1. Épicas del Proyecto

* **ÉPICA 1: Arquitectura Base y Conectividad Serie (Sprint 1)**
  * Creación de la ventana principal con estética industrial (tema oscuro).
  * Panel de escaneo y conexión automática/manual de puertos COM.
  * Lógica de control manual (botones para forzar colores e inspeccionar respuesta del LED).
* **ÉPICA 2: Captura de Video y Pipeline OpenCV (Sprint 2)**
  * Integración del flujo de la webcam en la interfaz Qt (hilo secundario QThread).
  * Despliegue de vistas de depuración (HSV y máscaras binarias combinadas).
* **ÉPICA 3: Calibrador HSV e Inferencia en Vivo (Sprint 3)**
  * Sliders de control interactivo para calibración en tiempo real de Verde, Amarillo y Rojo.
  * Ajuste en vivo de filtros anti-ruido (tamaño mínimo de píxeles y frames de estabilidad).
  * Persistencia de configuraciones (guardar y cargar perfiles de calibración).
* **ÉPICA 4: Modo Automático (Link), Estadísticas y Reportes (Sprint 4)**
  * Interruptor general de enlace automático (Link Mode).
  * Gráficos estadísticos dinámicos del historial de colores detectados.
  * Generador de informes técnicos y exportación de datos.

---

## 2. Plan de Sprints e Historias de Usuario

### Sprint 1: Conectividad y Base UI
* **Incremento esperado:** Aplicación base con interfaz oscura activa, escáner de puertos y control manual de LEDs funcional.
* **Historias de Usuario (Backlog):**
  * **US1.1:** Como usuario, quiero una interfaz gráfica moderna, oscura e industrial para poder visualizar los controles cómodamente en el laboratorio.
  * **US1.2:** Como usuario, quiero que la aplicación detecte los puertos COM disponibles en mi PC y me permita conectarme con un clic.
  * **US1.3:** Como usuario, quiero probar la conexión enviando comandos manuales de encendido/apagado al ESP32-C3 desde la UI (Fase 1 y Fase 2).

### Sprint 2: Integración de Visión Headless en GUI
* **Incremento esperado:** Reproducción estable de la cámara web integrada en un widget de la aplicación, sin bloquear la UI principal, junto con las vistas de depuración HSV.
* **Historias de Usuario (Backlog):**
  * **US2.1:** Como usuario, quiero ver el video de la cámara web directamente incrustado en el panel para no tener múltiples ventanas flotantes de OpenCV.
  * **US2.2:** Como usuario, quiero ver las máscaras binarias de detección en tiempo real para diagnosticar el comportamiento de la segmentación cromática.

### Sprint 3: Calibración y Persistencia
* **Incremento esperado:** Panel de control de rangos HSV activo con sliders interactivos que modifiquen la máscara en tiempo real y guarden los valores en un archivo JSON.
* **Historias de Usuario (Backlog):**
  * **US3.1:** Como usuario, quiero calibrar dinámicamente los rangos de Verde, Amarillo y Rojo mediante controles deslizantes (sliders) para adaptarme a cambios bruscos de iluminación.
  * **US3.2:** Como usuario, quiero regular el umbral de píxeles y la estabilidad de frames para suprimir interferencias de fondo en vivo.
  * **US3.3:** Como usuario, quiero guardar mi calibración para que se cargue automáticamente en la próxima sesión.

### Sprint 4: Enlace Automático e Informes
* **Incremento esperado:** Sistema de detección automática serie ("Link") enlazado con métricas, gráficos históricos integrados y exportación de PDF de prueba.
* **Historias de Usuario (Backlog):**
  * **US4.1:** Como usuario, quiero activar el "Modo Link" para que el detector tome el control del puerto serie y envíe comandos automáticos según lo que ve la cámara.
  * **US4.2:** Como usuario, quiero ver gráficos en tiempo real del uso de colores y contadores de tiempo activo para analizar el comportamiento.
  * **US4.3:** Como usuario, quiero exportar un reporte en formato PDF o de texto con las estadísticas de precisión y latencia para anexar a mi informe del TP2.
