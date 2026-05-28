import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QCheckBox

# Se necesita una instancia de QApplication
app = QApplication(sys.argv)

# Crea una ventana simple
widget = QWidget()
widget.setWindowTitle('Ventana con Estilo')
widget.resize(300, 300)

# Agrega widgets
label = QLabel('Escribe algo:', widget)
label.move(50, 50)

line_edit = QLineEdit(widget)
line_edit.move(50, 100)

button = QPushButton('Enviar', widget)
button.move(50, 150)

checkbox = QCheckBox('Acepto los términos', widget)
checkbox.move(50, 200)

# Aplica estilo a nivel de la aplicación
app.setStyleSheet("""
    QWidget {
        background-color: #f0f0f0;
    }
    QLabel {
        font-size: 16px;
        color: darkblue;
    }
    QLineEdit {
        background-color: white;
        border: 1px solid gray;
        padding: 5px;
        border-radius: 5px;
    }
    QPushButton {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px;
        font-size: 14px;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #45a049;
    }
    QCheckBox {
        font-size: 14px;
        color: darkgreen;
    }
""")

# Muestra la ventana
widget.show()

# Ejecuta el loop de eventos
sys.exit(app.exec_())
