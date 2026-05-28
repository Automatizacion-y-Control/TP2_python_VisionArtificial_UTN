import sys
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget

# Se necesita una instancia de QApplication
app = QApplication(sys.argv)

# Crea una ventana simple
widget = QWidget()
widget.setWindowTitle('Ventana básica')
widget.resize(800, 600)

# Agrega un QListWidget (lista de elementos)
list_widget = QListWidget(widget)
list_widget.setGeometry(10, 10, 200, 100)
list_widget.addItems(['Elemento 1', 'Elemento 2', 'Elemento 3'])

# Conecta el clic en un elemento de la lista
list_widget.itemClicked.connect(lambda item: print(f"Seleccionaste: {item.text()}"))
# Muestra la ventana
widget.show()

# Ejecuta el loop de eventos como si fuera el loop de arduino
sys.exit(app.exec_())
