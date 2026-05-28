import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton

# Se necesita una instancia de QApplication
app = QApplication(sys.argv)

# Crea una ventana simple
widget = QWidget()
widget.setWindowTitle('Ventana básica')
widget.resize(300, 200)

# Agrega un QLabel (etiqueta) dentro de la ventana
label = QLabel('¡Hola, eso es PyQt!', widget)
label.move(10, 10)  # posición x=10, y=10

# Agrega un QPushButton (botón) dentro de la ventana
button = QPushButton('Haz clic aquí', widget)
button.move(10, 40)  # Posición del botón

# Conecta el clic del botón a una función lambda que imprime un mensaje
button.clicked.connect(lambda: print("¡Botón clickeado!"))

# Muestra la ventana
widget.show()

# Ejecuta el loop de eventos como si fuera el loop de arduino
sys.exit(app.exec_())
