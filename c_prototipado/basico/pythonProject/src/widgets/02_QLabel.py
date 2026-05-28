import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

# Se necesita una instancia de QApplication
app = QApplication(sys.argv)

# Crea una ventana simple
widget = QWidget()
widget.setWindowTitle('Ventana básica')
widget.resize(300, 200)

# Agrega un QLabel (etiqueta) dentro de la ventana
label = QLabel('¡Hola, eso es PyQt!', widget)
label.move(10, 10)  # posición x=10, y=10

widget.show()

# Ejecuta el loop de eventos como si fuera el loop de arduino
sys.exit(app.exec_())
