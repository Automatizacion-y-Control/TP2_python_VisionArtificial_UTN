import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QPushButton

# Se necesita una instancia de QApplication
app = QApplication(sys.argv)

# Crea una ventana simple
widget = QWidget()
widget.setWindowTitle('Ventana básica')
widget.resize(800, 600)

# Función para abrir el cuadro de mensaje
def abrir_mensaje():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText('Este es un mensaje informativo.')
    msg.setWindowTitle('Mensaje')
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

# Agrega un botón para abrir el cuadro de mensaje
msg_button = QPushButton('Abrir mensaje', widget)
msg_button.move(10, 10)
msg_button.clicked.connect(abrir_mensaje)

# Muestra la ventana
widget.show()

# Ejecuta el loop de eventos como si fuera el loop de arduino
sys.exit(app.exec_())
