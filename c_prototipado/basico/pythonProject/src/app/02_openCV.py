import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QComboBox, QHBoxLayout, QSlider
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt

class ColorDetectorApp(QWidget):
    def __init__(self):
        super().__init__()

        # Colores predefinidos
        self.colors = {
            'Rojo': [([0, 120, 70], [10, 255, 255]), ([170, 120, 70], [180, 255, 255])],  # Doble rango para rojo
            'Verde': ([36, 100, 100], [86, 255, 255]),
            'Azul': ([94, 80, 2], [126, 255, 255]),
            'Amarillo': ([25, 70, 120], [30, 255, 255]),
            'Naranja': ([10, 100, 20], [25, 255, 255]),
        }
        self.selected_color = 'Rojo'
        self.brightness = 50
        self.contrast = 50

        # Inicializamos captura de video con OpenCV
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Actualizamos cada 30 ms

        # Llamada a la función para inicializar la interfaz gráfica
        self.initUI()

    def initUI(self):
        # Configuración de la ventana
        self.setWindowTitle('Detector de Color - OpenCV con PyQt')
        self.setGeometry(100, 100, 800, 600)

        # Layout principal
        layout = QVBoxLayout() # organiza widgets en una columna vertical, uno debajo del otro

        # Menú para seleccionar color
        self.color_menu = QComboBox(self)
        self.color_menu.addItems(self.colors.keys())
        self.color_menu.currentIndexChanged.connect(self.color_changed)

        # Botón para capturar imagen
        self.capture_button = QPushButton('Capturar Imagen', self)
        self.capture_button.clicked.connect(self.capture_image)

        # Slider para brillo
        self.brightness_slider = QSlider(Qt.Horizontal, self)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(50)
        self.brightness_slider.setTickInterval(10)
        self.brightness_slider.valueChanged.connect(self.adjust_brightness)

        # Slider para contraste
        self.contrast_slider = QSlider(Qt.Horizontal, self)
        self.contrast_slider.setRange(0, 100)
        self.contrast_slider.setValue(50)
        self.contrast_slider.setTickInterval(10)
        self.contrast_slider.valueChanged.connect(self.adjust_contrast)

        # Layout horizontal para el menú y botones
        top_layout = QHBoxLayout() # organiza widgets en una columna horizontal, uno debajo del otro
        top_layout.addWidget(self.color_menu)
        top_layout.addWidget(self.capture_button)

        # Layout para sliders
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(QLabel('Brillo'))
        slider_layout.addWidget(self.brightness_slider)
        slider_layout.addWidget(QLabel('Contraste'))
        slider_layout.addWidget(self.contrast_slider)

        # Área para mostrar la imagen en tiempo real
        self.video_label = QLabel(self)
        self.video_label.setFixedSize(1000, 480)

        # Agrega todo al layout principal
        layout.addLayout(top_layout)
        layout.addWidget(self.video_label)
        layout.addLayout(slider_layout)

        # Establece el layout principal
        self.setLayout(layout)

        # Estilos personalizados
        self.setStyleSheet("""
            QWidget {
                background-color: #2E2E2E;
            }
            QPushButton {
                background-color: #1E90FF;
                color: white;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1C86EE;
            }
            QComboBox {
                background-color: white;
                color: black;
                padding: 5px;
                font-size: 14px;
                border: 1px solid #1E90FF;
                border-radius: 5px;
            }
            QLabel {
                color: white;
                font-size: 18px;
            }
            QSlider {
                background-color: #2E2E2E;
            }
        """)

    def color_changed(self):
        # Cambia el color seleccionado
        self.selected_color = self.color_menu.currentText()

    def adjust_brightness(self, value):
        self.brightness = value

    def adjust_contrast(self, value):
        self.contrast = value

    def capture_image(self):
        # Capturar imagen en tiempo real de la cámara
        ret, frame = self.cap.read()
        if ret:
            cv2.imwrite('captura.jpg', frame)
            print('Imagen capturada y guardada como captura.jpg')

    def update_frame(self):
        # Captura frame de la cámara
        ret, frame = self.cap.read()
        if ret:
            # Ajustar brillo y contraste
            frame = self.adjust_image(frame, self.brightness, self.contrast)

            # Convertimos la imagen de BGR a HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Obtenemos los rangos de color seleccionados
            color_ranges = self.colors[self.selected_color]

            # Si el color seleccionado es el rojo (tiene más de un rango)
            if self.selected_color == 'Rojo':
                # Aplicamos ambas máscaras para el rojo
                lower1, upper1 = color_ranges[0]
                lower2, upper2 = color_ranges[1]
                mask1 = cv2.inRange(hsv, np.array(lower1), np.array(upper1))
                mask2 = cv2.inRange(hsv, np.array(lower2), np.array(upper2))
                mask = mask1 | mask2
            else:
                # Aplicamos una única máscara para otros colores
                lower, upper = color_ranges
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

            # Aplicamos la máscara al frame original
            result = cv2.bitwise_and(frame, frame, mask=mask)

            # Convertimos la imagen de BGR a RGB para PyQt
            rgb_image = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)

            # Mostramos la imagen procesada en el QLabel
            self.video_label.setPixmap(pixmap)

    def adjust_image(self, img, brightness, contrast):
        # Ajustamos brillo y contraste
        brightness = int((brightness - 50) * 2)
        contrast = int((contrast - 50) * 2)
        return cv2.convertScaleAbs(img, alpha=1 + contrast / 100, beta=brightness)

    def closeEvent(self, event):
        # Liberamos la cámara cuando se cierra la aplicación
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ColorDetectorApp()
    window.show()
    sys.exit(app.exec_())
