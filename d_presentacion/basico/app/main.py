"""
TP2 — Visión Artificial y Control de Color
Panel de Control Industrial — PyQt5

UTN FRC | Introducción a la Visión Artificial
Alumno: Cristian Gonzalo Vera | Legajo: 420581

Ejecución (desde PowerShell o CMD — NO desde Git Bash):
    py -3.13 main.py
"""

import os
import sys

# Silenciar logging de OpenCV (ObSensor/RealSense) antes de que se cargue la DLL
os.environ.setdefault("OPENCV_LOG_LEVEL", "OFF")

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

import config
import styles
from main_window import MainWindow


def main() -> None:
    # Soporte HiDPI para pantallas 4K / retina
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("TP2 — Visión Artificial y Control de Color")
    app.setOrganizationName("UTN FRC")

    # Aplicar hoja de estilos QSS global
    app.setStyleSheet(styles.DARK_QSS)

    # Intentar cargar perfil de calibración guardado
    config.load_config()

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
