# main.py
"""
Script principal del proyecto (Orquestador).
Inicializa la captura de video, ejecuta la detección en espacio HSV,
procesa el filtrado temporal y maneja la actuación serial.
"""

import cv2
import numpy as np
import time
import sys
from config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, DISPLAY_WINDOWS, COLOR_METADATA
from detector import ColorDetector
from filters import AntiNoiseFilter
from serial_comm import SerialCommunicator

def main():
    print("=" * 80)
    print("INICIANDO SISTEMA DE DETECCIÓN Y ACTUACIÓN DE COLOR (TP2)")
    print("Materia: Introducción a la Visión Artificial - UTN FRC")
    print("Alumno: Cristian Gonzalo Vera - Legajo: 420581")
    print("=" * 80)

    # 1. Inicializar componentes modulares
    detector = ColorDetector()
    anti_noise = AntiNoiseFilter()
    serial_comm = SerialCommunicator()

    # 2. Inicializar captura de video (Cámara Web)
    print(f"\nAbriendo cámara web (Índice: {CAMERA_INDEX})...")
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    # Configurar dimensiones de captura
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print(f"\n[ERROR CRÍTICO] No se pudo acceder a la cámara con índice {CAMERA_INDEX}.")
        print("Asegúrate de que la cámara esté conectada o que no esté siendo utilizada por otra aplicación.")
        serial_comm.close()
        sys.exit(1)

    print("Cámara abierta correctamente.")
    print("Instrucciones:")
    print("  - Coloca un objeto Rojo, Verde o Amarillo frente a la cámara.")
    print("  - Presiona la tecla 'q' en cualquiera de las ventanas de OpenCV para salir.")
    print("-" * 80)

    # Variables de medición de FPS y latido serial
    prev_time = 0
    fps = 0
    last_sent_time = 0

    try:
        while True:
            # 3. Leer frame de la cámara
            ret, frame = cap.read()
            if not ret or frame is None:
                print("[ERROR] Fallo al capturar frame de la cámara.")
                break

            # Clonar el frame original para anotaciones visuales
            annotated_frame = frame.copy()

            # 4. Procesamiento de imagen: Conversión HSV, Máscaras y Conteo de píxeles
            hsv, masks, pixel_counts = detector.process_frame(frame)

            # 5. Aplicar lógica de filtrado y decisión anti-ruido
            confirmed_color, should_send, active_candidate = anti_noise.filter_detection(pixel_counts)

            # 6. Actuación serial (si hay cambio o latido periódico para evitar timeout en el microcontrolador)
            current_time = time.time()
            if should_send or (current_time - last_sent_time >= 1.0):
                serial_comm.send_color(confirmed_color)
                last_sent_time = current_time

            # 7. Dibujar información en pantalla (Overlay gráfico en frame original)
            # Calcular FPS
            current_time = time.time()
            fps_delta = current_time - prev_time
            if fps_delta > 0:
                fps = int(1.0 / fps_delta)
            prev_time = current_time

            # Dibujar caja de información en la esquina superior izquierda
            overlay = annotated_frame.copy()
            cv2.rectangle(overlay, (10, 10), (320, 230), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, annotated_frame, 0.4, 0, annotated_frame)

            # Añadir textos
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(annotated_frame, f"TP2 - Vision & Control (UTN)", (20, 30), font, 0.6, (255, 255, 255), 2)
            cv2.putText(annotated_frame, f"FPS: {fps}", (20, 55), font, 0.5, (200, 200, 200), 1)
            
            # Estado del puerto serie
            serial_mode_str = "[MOCK - SIMULACION]" if serial_comm.is_mock else f"[PUERTO: {serial_comm.port}]"
            phase_str = f"Fase {serial_comm.phase}"
            cv2.putText(annotated_frame, f"Serie: {serial_mode_str} | {phase_str}", (20, 80), font, 0.5, (0, 255, 255), 1)

            # Conteo de píxeles en tiempo real
            cv2.putText(annotated_frame, f"Pixeles activos por color:", (20, 110), font, 0.5, (255, 255, 255), 1)
            cv2.putText(annotated_frame, f" - Rojo: {pixel_counts['rojo']} px", (20, 130), font, 0.45, (0, 0, 255), 1)
            cv2.putText(annotated_frame, f" - Verde: {pixel_counts['verde']} px", (20, 150), font, 0.45, (0, 255, 0), 1)
            cv2.putText(annotated_frame, f" - Amarillo: {pixel_counts['amarillo']} px", (20, 170), font, 0.45, (0, 255, 255), 1)

            # Color confirmado en grande
            metadata = COLOR_METADATA[confirmed_color]
            cv2.putText(annotated_frame, "COLOR ESTABLE:", (20, 200), font, 0.5, (255, 255, 255), 1)
            cv2.putText(annotated_frame, metadata["label"], (150, 205), font, 0.7, metadata["color_bgr"], 2)

            # Dibujar un círculo de color grande en la esquina superior derecha indicando el estado
            cv2.circle(annotated_frame, (580, 50), 30, (0, 0, 0), -1) # Borde negro
            cv2.circle(annotated_frame, (580, 50), 28, metadata["color_bgr"], -1) # Relleno de color

            # 8. Visualización de ventanas en tiempo real (si está habilitada)
            if DISPLAY_WINDOWS:
                # Redimensionar ventanas para visualización compacta y ordenada
                original_resized = cv2.resize(annotated_frame, (480, 360))
                hsv_resized = cv2.resize(hsv, (320, 240))

                # Crear stack horizontal de máscaras binarias de 320x240 cada una
                mask_rojo_small = cv2.resize(masks["rojo"], (240, 180))
                mask_verde_small = cv2.resize(masks["verde"], (240, 180))
                mask_amarillo_small = cv2.resize(masks["amarillo"], (240, 180))
                
                # Convertir máscaras grises a BGR para poder apilarlas y rotularlas con color
                mask_rojo_bgr = cv2.cvtColor(mask_rojo_small, cv2.COLOR_GRAY2BGR)
                mask_verde_bgr = cv2.cvtColor(mask_verde_small, cv2.COLOR_GRAY2BGR)
                mask_amarillo_bgr = cv2.cvtColor(mask_amarillo_small, cv2.COLOR_GRAY2BGR)

                # Rotular cada máscara
                cv2.putText(mask_rojo_bgr, "MASCARA ROJO", (10, 20), font, 0.45, (0, 0, 255), 1)
                cv2.putText(mask_verde_bgr, "MASCARA VERDE", (10, 20), font, 0.45, (0, 255, 0), 1)
                cv2.putText(mask_amarillo_bgr, "MASCARA AMARILLO", (10, 20), font, 0.45, (0, 255, 255), 1)

                masks_combined = np.hstack([mask_rojo_bgr, mask_verde_bgr, mask_amarillo_bgr])

                # Mostrar las tres vistas de depuración
                cv2.imshow("1. Original con Overlay - TP2", original_resized)
                cv2.imshow("2. Vista en Espacio HSV", hsv_resized)
                cv2.imshow("3. Analisis de Canales Cromáticos", masks_combined)

            # 9. Esperar tecla de salida 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n[SALIDA] Tecla 'q' presionada. Cerrando sistema...")
                break

    except KeyboardInterrupt:
        print("\n[SALIDA] Ejecución interrumpida por el usuario (Ctrl+C). Cerrando...")

    finally:
        # 10. Limpieza y liberación de recursos
        cap.release()
        serial_comm.close()
        cv2.destroyAllWindows()
        print("Recursos liberados. Programa finalizado correctamente.")

if __name__ == "__main__":
    main()
