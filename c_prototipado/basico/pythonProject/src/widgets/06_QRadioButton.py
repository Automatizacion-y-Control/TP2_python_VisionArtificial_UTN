import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QCheckBox, QRadioButton

# Se necesita una instancia de QApplication
app = QApplication(sys.argv)

# Crea una ventana simple
widget = QWidget()
widget.setWindowTitle('Ventana básica')
widget.resize(800, 600)

# Agrega un QLabel (etiqueta) dentro de la ventana
label = QLabel('Escribe algo:', widget)
label.move(10, 10)  # posición x=10, y=10

# Agrega un QLineEdit (campo de texto) dentro de la ventana, es como un input()
line_edit = QLineEdit(widget)
line_edit.move(100, 40)

# Agrega un QPushButton (botón) dentro de la ventana
button = QPushButton('Mostrar texto', widget)
button.move(100, 80)

# Agrega un QCheckBox (casilla de verificación) dentro de la ventana
checkbox = QCheckBox('Activar opción', widget)
checkbox.move(100, 120)

# Agrega los QRadioButtons (botones de opción)
radio1 = QRadioButton('Opción A', widget)
radio1.move(400, 40)
radio2 = QRadioButton('Opción B', widget)
radio2.move(400, 80)

# Conecta el clic del botón a una función que imprime el texto ingresado
button.clicked.connect(lambda: print(f"Texto ingresado: {line_edit.text()}"))

# Conecta el cambio de estado del checkbox a una función lambda
checkbox.stateChanged.connect(lambda: print(f"Checkbox {'activado' if checkbox.isChecked() else 'desactivado'}"))

# Conecta la selección de los radio buttons
radio1.toggled.connect(lambda: print('Opción A seleccionada' if radio1.isChecked() else 'Opción B seleccionada'))

# Muestra la ventana
widget.show()

# Ejecuta el loop de eventos como si fuera el loop de arduino
sys.exit(app.exec_())
