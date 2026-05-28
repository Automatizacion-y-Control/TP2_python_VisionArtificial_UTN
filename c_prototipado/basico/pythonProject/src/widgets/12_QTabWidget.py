import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTabWidget

# Se necesita una instancia de QApplication
app = QApplication(sys.argv)

# Crea una ventana simple
widget = QWidget()
widget.setWindowTitle('Ventana básica')
widget.resize(800, 600)

# Crea un QTabWidget (pestañas)
tab_widget = QTabWidget(widget)
tab_widget.setGeometry(10, 10, 400, 300)

# Crea las pestañas
tab1 = QWidget()
tab2 = QWidget()

# Agrega las pestañas al QTabWidget
tab_widget.addTab(tab1, "Pestaña 1")
tab_widget.addTab(tab2, "Pestaña 2")

# Muestra la ventana
widget.show()

# Ejecuta el loop de eventos como si fuera el loop de arduino
sys.exit(app.exec_())
