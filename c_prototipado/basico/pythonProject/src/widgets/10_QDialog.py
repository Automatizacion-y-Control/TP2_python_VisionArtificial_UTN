import sys
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QPushButton

# Se necesita una instancia de QApplication
app = QApplication(sys.argv)

# Crea una ventana simple
widget = QWidget()
widget.setWindowTitle('Ventana básica')
widget.resize(800, 600)

# Función para abrir el diálogo
def abrir_dialogo():
    dialogo = QDialog(widget)
    dialogo.setWindowTitle('Cuadro de diálogo')
    dialogo.setGeometry(400, 400, 200, 150)
    dialogo.exec_()

# Agrega un botón para abrir el diálogo
dialog_button = QPushButton('Abrir diálogo', widget)
dialog_button.move(10, 10)
dialog_button.clicked.connect(abrir_dialogo)

# Muestra la ventana
widget.show()

# Ejecuta el loop de eventos como si fuera el loop de arduino
sys.exit(app.exec_())
