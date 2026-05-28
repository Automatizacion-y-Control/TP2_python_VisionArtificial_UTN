import os
import sys
import cv2
import numpy as np
import time
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QPushButton,
    QComboBox, QHBoxLayout, QSlider, QFrame, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect, QSizePolicy
)
from PyQt5.QtGui import QImage, QPixmap, QColor, QIcon
from PyQt5.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize

# ── Rutas ─────────────────────────────────────────────────────────────────────
ICONS_DIR = os.path.join(os.path.dirname(__file__), "icons")

# ── Paleta de colores ─────────────────────────────────────────────────────────
BG_BASE   = "#0A0E14"
BG_PANEL  = "#12171F"
BG_CARD   = "#1A2030"
ACCENT    = "#4D9EFF"
SUCCESS   = "#3DDC84"
WARNING   = "#FFB830"
DANGER    = "#FF4D6A"
PURPLE    = "#A78BFA"
TEXT_PRI  = "#E8EEF7"
TEXT_SEC  = "#7A8899"
BORDER    = "#252E40"

COLOR_MAP = {
    "Rojo":     "#FF4444",
    "Verde":    "#44FF88",
    "Azul":     "#4488FF",
    "Amarillo": "#FFEE44",
    "Naranja":  "#FF9944",
}


# ── Helpers de íconos ─────────────────────────────────────────────────────────

def _icon(name: str, size: int = 18) -> QIcon:
    path = os.path.join(ICONS_DIR, f"icon_{name}.png")
    px = QPixmap(path).scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    return QIcon(px)


def _pixmap(name: str, size: int = 16) -> QPixmap:
    path = os.path.join(ICONS_DIR, f"icon_{name}.png")
    return QPixmap(path).scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)


# ── Componentes personalizados ────────────────────────────────────────────────

class GlowButton(QPushButton):
    """Botón con animación de brillo (glow) al pasar el cursor."""

    def __init__(self, text, color=ACCENT, icon_name=None, parent=None):
        super().__init__(text, parent)
        self._color = color
        self.setCursor(Qt.PointingHandCursor)

        if icon_name:
            self.setIcon(_icon(icon_name, 18))
            self.setIconSize(QSize(18, 18))

        self._glow = QGraphicsDropShadowEffect(self)
        self._glow.setBlurRadius(0)
        self._glow.setColor(QColor(color))
        self._glow.setOffset(0, 0)
        self.setGraphicsEffect(self._glow)

        self._in_anim = QPropertyAnimation(self._glow, b"blurRadius", self)
        self._in_anim.setDuration(160)
        self._in_anim.setEasingCurve(QEasingCurve.OutCubic)

        self._out_anim = QPropertyAnimation(self._glow, b"blurRadius", self)
        self._out_anim.setDuration(240)
        self._out_anim.setEasingCurve(QEasingCurve.InCubic)

        self._apply_style()

    def _apply_style(self):
        c = QColor(self._color)
        dark  = QColor(max(0, c.red()-40),   max(0, c.green()-40),   max(0, c.blue()-40))
        light = QColor(min(255, c.red()+30), min(255, c.green()+30), min(255, c.blue()+30))
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 {self._color}, stop:1 {dark.name()});
                color: #FFFFFF;
                border: 1px solid {light.name()}44;
                border-radius: 9px;
                padding: 9px 18px 9px 14px;
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: 600;
                min-height: 36px;
                letter-spacing: 0.3px;
                text-align: left;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 {light.name()}, stop:1 {self._color});
            }}
            QPushButton:pressed {{
                background: {dark.name()};
                padding: 10px 17px 8px 15px;
            }}
            QPushButton:disabled {{
                background: #252E40;
                color: #4A5568;
                border-color: transparent;
            }}
        """)

    def enterEvent(self, e):
        self._out_anim.stop()
        self._in_anim.setStartValue(self._glow.blurRadius())
        self._in_anim.setEndValue(22)
        self._in_anim.start()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._in_anim.stop()
        self._out_anim.setStartValue(self._glow.blurRadius())
        self._out_anim.setEndValue(0)
        self._out_anim.start()
        super().leaveEvent(e)


class SliderRow(QWidget):
    """Slider con ícono PNG, etiqueta y badge de valor en tiempo real."""
    valueChanged = pyqtSignal(int)

    def __init__(self, label, icon_name, min_v=0, max_v=100, val=50, parent=None):
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        # Ícono
        icon_lbl = QLabel()
        icon_lbl.setPixmap(_pixmap(icon_name, 14))
        icon_lbl.setFixedSize(18, 18)
        icon_lbl.setAlignment(Qt.AlignCenter)

        # Texto
        text_lbl = QLabel(label)
        text_lbl.setFixedWidth(66)
        text_lbl.setStyleSheet(f"color:{TEXT_SEC}; font-size:12px; font-weight:500;")

        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(min_v, max_v)
        self.slider.setValue(val)
        self.slider.setCursor(Qt.PointingHandCursor)
        self.slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 5px;
                background: {BG_CARD};
                border-radius: 3px;
            }}
            QSlider::sub-page:horizontal {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #1E4D8A, stop:1 {ACCENT});
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {ACCENT};
                border: 2px solid #1A3A6A;
                width: 15px;
                height: 15px;
                margin: -6px 0;
                border-radius: 8px;
            }}
            QSlider::handle:horizontal:hover  {{ background: #80BFFF; border-color: {ACCENT}; }}
            QSlider::handle:horizontal:pressed {{ background: #2060D0; }}
        """)
        self.slider.valueChanged.connect(self._emit)

        # Badge valor
        self.badge = QLabel(str(val))
        self.badge.setFixedWidth(34)
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setStyleSheet(f"""
            color: {ACCENT}; font-size:11px; font-weight:700;
            background: {BG_CARD}; border:1px solid {BORDER};
            border-radius:5px; padding:2px;
        """)

        row.addWidget(icon_lbl)
        row.addWidget(text_lbl)
        row.addWidget(self.slider, 1)
        row.addWidget(self.badge)

    def _emit(self, v):
        self.badge.setText(str(v))
        self.valueChanged.emit(v)

    def value(self):
        return self.slider.value()


class FlashOverlay(QWidget):
    """Destello blanco sobre el video al capturar."""
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setStyleSheet("background: white; border-radius: 8px;")
        self.hide()

        self._eff = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._eff)
        self._eff.setOpacity(0)

        self._anim = QPropertyAnimation(self._eff, b"opacity", self)
        self._anim.setDuration(380)
        self._anim.setKeyValueAt(0.0, 0.85)
        self._anim.setKeyValueAt(1.0, 0.0)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.finished.connect(self.hide)

    def flash(self):
        self.resize(self.parent().size())
        self.move(0, 0)
        self.show()
        self.raise_()
        self._anim.stop()
        self._eff.setOpacity(0.85)
        self._anim.start()


class Toast(QWidget):
    """Notificación flotante con ícono, texto y desvanecimiento automático."""
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.hide()

        self._eff = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._eff)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 16, 8)
        layout.setSpacing(8)

        self._icon_lbl = QLabel()
        self._icon_lbl.setFixedSize(16, 16)
        self._icon_lbl.setAlignment(Qt.AlignCenter)

        self._text_lbl = QLabel()
        self._text_lbl.setStyleSheet("""
            font-family: 'Segoe UI'; font-size: 13px;
            font-weight: 700; color: #0A0E14;
        """)

        layout.addWidget(self._icon_lbl)
        layout.addWidget(self._text_lbl)

        self._fade = QPropertyAnimation(self._eff, b"opacity", self)
        self._fade.setDuration(500)
        self._fade.setStartValue(1.0)
        self._fade.setEndValue(0.0)
        self._fade.setEasingCurve(QEasingCurve.InCubic)
        self._fade.finished.connect(self.hide)

        self._delay = QTimer()
        self._delay.setSingleShot(True)
        self._delay.timeout.connect(self._fade.start)

    def notify(self, msg, icon_name=None, color=SUCCESS, ms=2400):
        self._text_lbl.setText(msg)
        if icon_name:
            self._icon_lbl.setPixmap(_pixmap(icon_name, 16))
            self._icon_lbl.show()
        else:
            self._icon_lbl.hide()

        self.setStyleSheet(f"""
            QWidget {{
                background: {color};
                border-radius: 10px;
            }}
        """)
        self._fade.stop()
        self._eff.setOpacity(1.0)
        self.adjustSize()
        p = self.parent()
        self.move((p.width() - self.width()) // 2, 16)
        self.show()
        self.raise_()
        self._delay.start(ms)


class Divider(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background: {BORDER}; border: none;")


# ── Aplicación principal ──────────────────────────────────────────────────────

class ColorDetectorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.colors = {
            "Rojo":     [([0, 120, 70], [10, 255, 255]), ([170, 120, 70], [180, 255, 255])],
            "Verde":    ([36, 100, 100], [86, 255, 255]),
            "Azul":     ([94, 80, 2],   [126, 255, 255]),
            "Amarillo": ([25, 70, 120],  [30, 255, 255]),
            "Naranja":  ([10, 100, 20],  [25, 255, 255]),
        }
        self.selected_color = "Rojo"
        self.brightness = 50
        self.contrast = 50
        self.paused = False

        self._fps = 0.0
        self._frame_count = 0
        self._fps_last = time.time()

        # Íconos de pausa/play precargados para el toggle
        self._ico_pause = _icon("pause", 18)
        self._ico_play  = _icon("play",  18)

        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)
        self.timer.start(30)

        self._build_ui()

    # ── Construcción de la UI ─────────────────────────────────────────────────

    def _build_ui(self):
        self.setWindowTitle("Color Detector  ·  OpenCV + PyQt5")
        self.setMinimumSize(1020, 640)
        self.resize(1120, 700)
        self.setStyleSheet(f"""
            QWidget {{ background: {BG_BASE}; font-family: 'Segoe UI'; }}
            QToolTip {{
                background: {BG_CARD}; color: {TEXT_PRI};
                border: 1px solid {BORDER}; border-radius: 5px;
                padding: 4px 8px; font-size: 12px;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._build_sidebar())
        body.addWidget(self._build_video_area(), 1)
        root.addLayout(body, 1)

    def _build_header(self):
        header = QFrame()
        header.setFixedHeight(54)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #0F1924, stop:1 {BG_BASE});
                border-bottom: 1px solid {BORDER};
            }}
        """)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(0)

        # Logo ícono real
        logo_lbl = QLabel()
        logo_lbl.setPixmap(_pixmap("logo", 24))
        logo_lbl.setFixedSize(28, 28)
        logo_lbl.setAlignment(Qt.AlignCenter)

        title = QLabel("Color Detector")
        title.setStyleSheet(f"""
            color: {TEXT_PRI}; font-size: 17px; font-weight: 700;
            letter-spacing: 0.5px; margin-left: 8px;
        """)

        sub = QLabel("OpenCV · PyQt5")
        sub.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; margin-left: 10px;")

        self._cam_dot = QLabel("●")
        self._cam_dot.setStyleSheet(f"color: {SUCCESS}; font-size: 14px;")
        self._cam_lbl = QLabel("Cámara activa")
        self._cam_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; margin-left: 5px;")

        self._fps_badge = QLabel("FPS: --")
        self._fps_badge.setStyleSheet(f"""
            color: {ACCENT}; font-size: 12px; font-weight: 700;
            background: #0F1924; border: 1px solid {BORDER};
            border-radius: 5px; padding: 3px 10px; margin-left: 16px;
        """)

        layout.addWidget(logo_lbl)
        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addStretch()
        layout.addWidget(self._cam_dot)
        layout.addWidget(self._cam_lbl)
        layout.addWidget(self._fps_badge)

        return header

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(252)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background: {BG_PANEL};
                border-right: 1px solid {BORDER};
            }}
        """)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(12)

        # ── Filtro de color ───────────────────────────────────────
        self._section(layout, "FILTRO DE COLOR")

        color_row = QHBoxLayout()
        color_row.setSpacing(8)
        self._dot_lbl = QLabel("●")
        self._dot_lbl.setStyleSheet(f"color: {COLOR_MAP['Rojo']}; font-size: 20px;")
        self._dot_lbl.setFixedWidth(24)

        self.color_combo = QComboBox()
        self.color_combo.addItems(self.colors.keys())
        self.color_combo.setCursor(Qt.PointingHandCursor)
        self.color_combo.setStyleSheet(f"""
            QComboBox {{
                background: {BG_CARD}; color: {TEXT_PRI};
                border: 1px solid {BORDER}; border-radius: 8px;
                padding: 7px 12px; font-size: 13px; font-weight: 500;
            }}
            QComboBox:hover {{ border-color: {ACCENT}; }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox QAbstractItemView {{
                background: {BG_CARD}; color: {TEXT_PRI};
                border: 1px solid {BORDER}; border-radius: 6px;
                selection-background-color: {ACCENT};
                selection-color: #FFFFFF;
                outline: none; padding: 4px;
            }}
        """)
        self.color_combo.currentIndexChanged.connect(self._color_changed)
        color_row.addWidget(self._dot_lbl)
        color_row.addWidget(self.color_combo, 1)
        layout.addLayout(color_row)

        layout.addWidget(Divider())

        # ── Ajustes de imagen ─────────────────────────────────────
        self._section(layout, "AJUSTES DE IMAGEN")

        self.brightness_slider = SliderRow("Brillo", "sun", val=50)
        self.brightness_slider.valueChanged.connect(lambda v: setattr(self, "brightness", v))

        self.contrast_slider = SliderRow("Contraste", "contrast", val=50)
        self.contrast_slider.valueChanged.connect(lambda v: setattr(self, "contrast", v))

        layout.addWidget(self.brightness_slider)
        layout.addWidget(self.contrast_slider)

        layout.addWidget(Divider())

        # ── Controles ─────────────────────────────────────────────
        self._section(layout, "CONTROLES")

        self.capture_btn = GlowButton("Capturar imagen", color=ACCENT, icon_name="camera")
        self.capture_btn.setToolTip("Guardar el frame actual como .jpg")
        self.capture_btn.clicked.connect(self._capture)

        self.pause_btn = GlowButton("Pausar cámara", color=PURPLE, icon_name="pause")
        self.pause_btn.setToolTip("Pausar / reanudar la transmisión")
        self.pause_btn.clicked.connect(self._toggle_pause)

        self.reset_btn = GlowButton("Resetear ajustes", color="#6B7280", icon_name="reset")
        self.reset_btn.setToolTip("Volver brillo y contraste a 50")
        self.reset_btn.clicked.connect(self._reset_sliders)

        layout.addWidget(self.capture_btn)
        layout.addWidget(self.pause_btn)
        layout.addWidget(self.reset_btn)

        layout.addStretch()

        # ── Chip de filtro activo ─────────────────────────────────
        self._filter_info = QLabel("Filtro activo: Rojo")
        self._filter_info.setAlignment(Qt.AlignCenter)
        self._filter_info.setStyleSheet(f"""
            color: {TEXT_SEC}; font-size: 11px;
            background: {BG_CARD}; border: 1px solid {BORDER};
            border-radius: 6px; padding: 5px;
        """)
        layout.addWidget(self._filter_info)

        return sidebar

    def _build_video_area(self):
        container = QFrame()
        container.setStyleSheet(f"QFrame {{ background: {BG_BASE}; }}")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(14, 14, 14, 10)
        layout.setSpacing(8)

        # Marco del video
        video_frame = QFrame()
        video_frame.setStyleSheet(f"""
            QFrame {{
                background: #000000;
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
        """)
        vf_layout = QVBoxLayout(video_frame)
        vf_layout.setContentsMargins(3, 3, 3, 3)

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setStyleSheet("background: #000000; border-radius: 8px;")
        vf_layout.addWidget(self.video_label)

        # Sombra bajo el marco
        shadow = QGraphicsDropShadowEffect(video_frame)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(ACCENT).darker(400))
        shadow.setOffset(0, 6)
        video_frame.setGraphicsEffect(shadow)

        layout.addWidget(video_frame, 1)
        layout.addWidget(self._build_status_bar())

        self._flash = FlashOverlay(self.video_label)
        self._toast = Toast(self)

        return container

    def _build_status_bar(self):
        bar = QFrame()
        bar.setFixedHeight(30)
        bar.setStyleSheet(f"""
            QFrame {{
                background: {BG_PANEL};
                border: 1px solid {BORDER};
                border-radius: 7px;
            }}
        """)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(16)

        self._res_lbl   = self._chip("Resolución: --")
        self._filter_lbl = self._chip("Filtro: Rojo")
        self._live_lbl  = self._chip("● En vivo", color=SUCCESS)

        layout.addWidget(self._res_lbl)
        layout.addWidget(self._filter_lbl)
        layout.addStretch()
        layout.addWidget(self._live_lbl)

        return bar

    # ── Helpers de UI ─────────────────────────────────────────────────────────

    def _section(self, layout, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            color: {TEXT_SEC}; font-size: 10px; font-weight: 700;
            letter-spacing: 1.3px; padding-bottom: 2px;
        """)
        layout.addWidget(lbl)

    def _chip(self, text, color=TEXT_SEC):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {color}; font-size: 11px;")
        return lbl

    # ── Lógica de eventos ─────────────────────────────────────────────────────

    def _color_changed(self):
        name = self.color_combo.currentText()
        self.selected_color = name
        c = COLOR_MAP.get(name, ACCENT)
        self._dot_lbl.setStyleSheet(f"color: {c}; font-size: 20px;")
        self._filter_lbl.setText(f"Filtro: {name}")
        self._filter_info.setText(f"Filtro activo: {name}")

    def _capture(self):
        ret, frame = self.cap.read()
        if ret:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"captura_{ts}.jpg"
            cv2.imwrite(fname, frame)
            self._flash.flash()
            self._toast.notify(f"Guardado: {fname}", icon_name="check", color=SUCCESS)
        else:
            self._toast.notify("Cámara no disponible", icon_name="error", color=DANGER)

    def _toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.timer.stop()
            self.pause_btn.setIcon(self._ico_play)
            self.pause_btn.setText("Reanudar cámara")
            self._cam_dot.setStyleSheet(f"color: {WARNING}; font-size: 14px;")
            self._cam_lbl.setText("Pausado")
            self._live_lbl.setText("⏸ Pausado")
            self._live_lbl.setStyleSheet(f"color: {WARNING}; font-size: 11px;")
        else:
            self.timer.start(30)
            self.pause_btn.setIcon(self._ico_pause)
            self.pause_btn.setText("Pausar cámara")
            self._cam_dot.setStyleSheet(f"color: {SUCCESS}; font-size: 14px;")
            self._cam_lbl.setText("Cámara activa")
            self._live_lbl.setText("● En vivo")
            self._live_lbl.setStyleSheet(f"color: {SUCCESS}; font-size: 11px;")

    def _reset_sliders(self):
        self.brightness_slider.slider.setValue(50)
        self.contrast_slider.slider.setValue(50)
        self._toast.notify("Ajustes restablecidos", icon_name="reset", color=WARNING)

    # ── Loop de video ─────────────────────────────────────────────────────────

    def _update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        self._frame_count += 1
        now = time.time()
        elapsed = now - self._fps_last
        if elapsed >= 0.5:
            self._fps = self._frame_count / elapsed
            self._frame_count = 0
            self._fps_last = now
            self._fps_badge.setText(f"FPS: {self._fps:.0f}")

        frame = self._adjust(frame, self.brightness, self.contrast)
        h, w = frame.shape[:2]
        self._res_lbl.setText(f"Resolución: {w}×{h}")

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        ranges = self.colors[self.selected_color]

        if self.selected_color == "Rojo":
            l1, u1 = ranges[0]
            l2, u2 = ranges[1]
            mask = (cv2.inRange(hsv, np.array(l1), np.array(u1)) |
                    cv2.inRange(hsv, np.array(l2), np.array(u2)))
        else:
            lower, upper = ranges
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))

        result = cv2.bitwise_and(frame, frame, mask=mask)
        rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img).scaled(
            self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.video_label.setPixmap(pixmap)

    def _adjust(self, img, brightness, contrast):
        b = int((brightness - 50) * 2)
        c = int((contrast - 50) * 2)
        return cv2.convertScaleAbs(img, alpha=1 + c / 100, beta=b)

    def resizeEvent(self, event):
        if hasattr(self, "_toast") and self._toast.isVisible():
            self._toast.move((self.width() - self._toast.width()) // 2, 16)
        super().resizeEvent(event)

    def closeEvent(self, event):
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ColorDetectorApp()
    window.show()
    sys.exit(app.exec_())
