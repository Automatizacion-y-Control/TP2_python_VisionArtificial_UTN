import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout
from PyQt5.QtGui import QPixmap

class AdivinadorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Configuración de la ventana
        self.setWindowTitle('Adivinador')
        self.setGeometry(100, 100, 400, 500)

        # Layout
        layout = QVBoxLayout()

        # Imagen del genio
        self.image_label = QLabel(self)
        pixmap = QPixmap('genio.png')  # Imagen del genio (carga la imagen desde el archivo)
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        # Label para pedir al usuario que ingrese algo
        self.instruction_label = QLabel('Escribe lo que estas pensando y lo adivinaré', self)
        self.instruction_label.setStyleSheet("font-size: 18px; color: #1E90FF; font-weight: bold;")
        self.instruction_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.instruction_label)

        # Campo de texto
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Escribe aquí la palabra en la que piensas")
        self.input_field.setStyleSheet("""
            background-color: white;
            border: 2px solid #1E90FF;
            padding: 10px;
            border-radius: 10px;
            font-size: 16px;
        """)
        layout.addWidget(self.input_field)

        # Botón para confirmar
        self.submit_button = QPushButton('Adivinar', self)
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #1E90FF;
                color: white;
                border: none;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1C86EE;
            }
        """)
        self.submit_button.clicked.connect(self.show_input)
        layout.addWidget(self.submit_button)

        # Label para mostrar el texto ingresado
        self.result_label = QLabel('', self)
        self.result_label.setStyleSheet("font-size: 18px; color: #333; font-weight: bold;")
        self.result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_label)

        # Establecer el layout
        self.setLayout(layout)

    def show_input(self):
        # Mostrar el texto ingresado por el usuario
        user_input = self.input_field.text()
        if user_input:
            self.result_label.setText(f"Estabas pensando en: {user_input}")
        else:
            self.result_label.setText("Por favor, ingresa algo.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AdivinadorApp()
    window.show()
    sys.exit(app.exec_())
