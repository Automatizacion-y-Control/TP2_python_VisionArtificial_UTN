import os
import sys
import random
import time
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QFrame, QStackedWidget, QSlider, QScrollArea, QGraphicsDropShadowEffect,
    QSizePolicy, QButtonGroup, QAbstractButton, QSpacerItem
)
from PyQt5.QtGui import (
    QColor, QPainter, QPen, QLinearGradient, QFont,
    QPainterPath, QPolygonF, QIcon, QPixmap
)
from PyQt5.QtCore import (
    QTimer, Qt, QPropertyAnimation, QEasingCurve, pyqtSignal,
    pyqtProperty, QRectF, QPointF, QSize
)

# ── Paleta ────────────────────────────────────────────────────────────────────
BG_BASE  = "#0C1017"
BG_PANEL = "#131A24"
BG_CARD  = "#1A2332"
ACCENT   = "#00D4FF"
SUCCESS  = "#00E096"
WARNING  = "#FFB020"
DANGER   = "#FF4747"
PURPLE   = "#A78BFA"
TEXT_PRI = "#E2E8F0"
TEXT_SEC = "#64748B"
BORDER   = "#1E3A5F"

ICONS_DIR = os.path.join(os.path.dirname(__file__), "icons")


def _icon(name: str, size: int = 20) -> QIcon:
    px = QPixmap(os.path.join(ICONS_DIR, f"{name}.png")).scaled(
        size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    return QIcon(px)


def _pixmap(name: str, size: int = 16) -> QPixmap:
    return QPixmap(os.path.join(ICONS_DIR, f"{name}.png")).scaled(
        size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)


def _rand_walk(value, amplitude=0.03, mn=0, mx=9999):
    return max(mn, min(mx, value * (1 + random.uniform(-amplitude, amplitude))))


# ── Divider ───────────────────────────────────────────────────────────────────
class Divider(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background:{BORDER}; border:none;")


# ── NavButton ─────────────────────────────────────────────────────────────────
class NavButton(QPushButton):
    def __init__(self, text, icon_name, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setIcon(_icon(icon_name, 22))
        self.setIconSize(QSize(22, 22))
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(50)
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SEC};
                border: none;
                border-left: 3px solid transparent;
                padding: 0 20px;
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: 500;
                text-align: left;
            }}
            QPushButton:hover {{
                background: {BG_CARD};
                color: {TEXT_PRI};
                border-left: 3px solid {BORDER};
            }}
            QPushButton:checked {{
                background: {BG_CARD};
                color: {ACCENT};
                border-left: 3px solid {ACCENT};
                font-weight: 700;
            }}
        """)


# ── GlowButton ────────────────────────────────────────────────────────────────
class GlowButton(QPushButton):
    def __init__(self, text, color=ACCENT, icon_name=None, parent=None):
        super().__init__(text, parent)
        self._color = color
        self.setCursor(Qt.PointingHandCursor)
        if icon_name:
            self.setIcon(_icon(icon_name, 16))
            self.setIconSize(QSize(16, 16))

        self._glow = QGraphicsDropShadowEffect(self)
        self._glow.setBlurRadius(0)
        self._glow.setColor(QColor(color))
        self._glow.setOffset(0, 0)
        self.setGraphicsEffect(self._glow)

        self._in  = QPropertyAnimation(self._glow, b"blurRadius", self)
        self._in.setDuration(160); self._in.setEasingCurve(QEasingCurve.OutCubic)
        self._out = QPropertyAnimation(self._glow, b"blurRadius", self)
        self._out.setDuration(240); self._out.setEasingCurve(QEasingCurve.InCubic)

        c = QColor(color)
        dk = QColor(max(0,c.red()-40), max(0,c.green()-40), max(0,c.blue()-40))
        lt = QColor(min(255,c.red()+30), min(255,c.green()+30), min(255,c.blue()+30))
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 {color}, stop:1 {dk.name()});
                color:#FFF; border:none; border-radius:8px;
                padding:8px 18px; font-family:'Segoe UI';
                font-size:12px; font-weight:600; min-height:32px;
            }}
            QPushButton:hover {{ background:{lt.name()}; }}
            QPushButton:pressed {{ background:{dk.name()}; }}
            QPushButton:disabled {{ background:#1E3A5F; color:#4A5568; }}
        """)

    def enterEvent(self, e):
        self._out.stop(); self._in.setStartValue(self._glow.blurRadius())
        self._in.setEndValue(20); self._in.start(); super().enterEvent(e)

    def leaveEvent(self, e):
        self._in.stop(); self._out.setStartValue(self._glow.blurRadius())
        self._out.setEndValue(0); self._out.start(); super().leaveEvent(e)


# ── FilterButton ──────────────────────────────────────────────────────────────
class FilterButton(QPushButton):
    def __init__(self, text, color=TEXT_SEC, parent=None):
        super().__init__(text, parent)
        self._color = color
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(30)
        self._apply()

    def _apply(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background:{BG_CARD}; color:{TEXT_SEC};
                border:1px solid {BORDER}; border-radius:6px;
                padding:0 14px; font-size:12px; font-weight:500;
            }}
            QPushButton:hover {{ border-color:{self._color}; color:{TEXT_PRI}; }}
            QPushButton:checked {{
                background:{self._color}22; color:{self._color};
                border-color:{self._color}; font-weight:700;
            }}
        """)


# ── ToggleSwitch ──────────────────────────────────────────────────────────────
class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self.setFixedSize(52, 28)
        self.setCursor(Qt.PointingHandCursor)
        self._checked = checked
        self._pos = 26.0 if checked else 4.0

        self._anim = QPropertyAnimation(self, b"handle_x")
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    @pyqtProperty(float)
    def handle_x(self):
        return self._pos

    @handle_x.setter
    def handle_x(self, v):
        self._pos = v
        self.update()

    def is_checked(self):
        return self._checked

    def set_checked(self, val):
        self._checked = val
        self._anim.setStartValue(self._pos)
        self._anim.setEndValue(26.0 if val else 4.0)
        self._anim.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        # Track
        track = QColor(ACCENT) if self._checked else QColor(BORDER)
        p.setBrush(track)
        p.drawRoundedRect(0, 4, 52, 20, 10, 10)
        # Handle shadow
        p.setBrush(QColor(0, 0, 0, 60))
        p.drawEllipse(int(self._pos)+1, 3, 22, 22)
        # Handle
        p.setBrush(QColor("#FFFFFF"))
        p.drawEllipse(int(self._pos), 2, 22, 22)

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self._anim.setStartValue(self._pos)
        self._anim.setEndValue(26.0 if self._checked else 4.0)
        self._anim.start()
        self.toggled.emit(self._checked)


# ── LEDIndicator ──────────────────────────────────────────────────────────────
class LEDIndicator(QWidget):
    def __init__(self, color=SUCCESS, parent=None):
        super().__init__(parent)
        self.setFixedSize(14, 14)
        self._on = True
        self._color = QColor(color)

        self._glow = QGraphicsDropShadowEffect(self)
        self._glow.setColor(self._color)
        self._glow.setOffset(0, 0)
        self._glow.setBlurRadius(6)
        self.setGraphicsEffect(self._glow)

        self._pulse = QPropertyAnimation(self._glow, b"blurRadius", self)
        self._pulse.setDuration(1100)
        self._pulse.setStartValue(4); self._pulse.setEndValue(14)
        self._pulse.setEasingCurve(QEasingCurve.InOutSine)
        self._pulse.setLoopCount(-1)
        self._pulse.start()

    def set_state(self, on: bool, color: str = None):
        self._on = on
        if color:
            self._color = QColor(color)
            self._glow.setColor(self._color)
        if on:
            self._pulse.start()
        else:
            self._pulse.stop()
            self._glow.setBlurRadius(0)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(self._color if self._on else QColor(BORDER))
        p.drawEllipse(2, 2, 10, 10)


# ── Sparkline ─────────────────────────────────────────────────────────────────
class Sparkline(QWidget):
    def __init__(self, data, color=ACCENT, show_axes=False, parent=None):
        super().__init__(parent)
        self._data = list(data)
        self._color = QColor(color)
        self._show_axes = show_axes
        if not show_axes:
            self.setFixedHeight(32)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed if not show_axes else QSizePolicy.Expanding)

    def set_data(self, data):
        self._data = list(data)
        self.update()

    def paintEvent(self, event):
        if len(self._data) < 2:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        pad_l = 36 if self._show_axes else 4
        pad_r = 8; pad_t = 8; pad_b = 20 if self._show_axes else 4
        w = self.width() - pad_l - pad_r
        h = self.height() - pad_t - pad_b
        mn, mx = min(self._data), max(self._data)
        if mn == mx:
            mn -= 1; mx += 1

        def pt(i):
            x = pad_l + i / (len(self._data)-1) * w
            y = pad_t + (1 - (self._data[i]-mn)/(mx-mn)) * h
            return QPointF(x, y)

        pts = [pt(i) for i in range(len(self._data))]

        if self._show_axes:
            # Grid lines
            p.setPen(QPen(QColor(BORDER), 1, Qt.DashLine))
            for i in range(5):
                y = pad_t + i * h / 4
                p.drawLine(pad_l, int(y), pad_l + w, int(y))
            # Y labels
            p.setPen(QColor(TEXT_SEC))
            p.setFont(QFont("Segoe UI", 8))
            for i in range(5):
                y = pad_t + i * h / 4
                val = mx - i * (mx - mn) / 4
                p.drawText(QRectF(0, y-8, pad_l-4, 16), Qt.AlignRight | Qt.AlignVCenter, f"{val:.0f}")

        # Fill gradient
        fill = QPainterPath()
        fill.moveTo(QPointF(pts[0].x(), pad_t + h))
        fill.lineTo(pts[0])
        for i in range(1, len(pts)-1):
            mx_x = (pts[i].x() + pts[i+1].x()) / 2
            mx_y = (pts[i].y() + pts[i+1].y()) / 2
            fill.quadTo(pts[i], QPointF(mx_x, mx_y))
        fill.lineTo(pts[-1])
        fill.lineTo(QPointF(pts[-1].x(), pad_t + h))
        fill.closeSubpath()

        grad = QLinearGradient(0, pad_t, 0, pad_t + h)
        c = self._color
        grad.setColorAt(0, QColor(c.red(), c.green(), c.blue(), 70))
        grad.setColorAt(1, QColor(c.red(), c.green(), c.blue(), 0))
        p.fillPath(fill, grad)

        # Smooth line
        line = QPainterPath()
        line.moveTo(pts[0])
        for i in range(1, len(pts)-1):
            mx_x = (pts[i].x() + pts[i+1].x()) / 2
            mx_y = (pts[i].y() + pts[i+1].y()) / 2
            line.quadTo(pts[i], QPointF(mx_x, mx_y))
        line.lineTo(pts[-1])
        p.setPen(QPen(self._color, 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.drawPath(line)

        # Last value dot
        p.setBrush(self._color)
        p.setPen(QPen(QColor(BG_CARD), 2))
        p.drawEllipse(pts[-1], 4, 4)


# ── CircularGauge ─────────────────────────────────────────────────────────────
class CircularGauge(QWidget):
    def __init__(self, title, value, max_val, unit, icon_name, color=ACCENT, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 210)
        self._title = title
        self._max = max_val
        self._unit = unit
        self._color = color
        self._val = 0.0
        self._icon_px = _pixmap(icon_name, 20)

        self._anim = QPropertyAnimation(self, b"gauge_value")
        self._anim.setDuration(1400)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(float(value))
        self._anim.start()

    @pyqtProperty(float)
    def gauge_value(self):
        return self._val

    @gauge_value.setter
    def gauge_value(self, v):
        self._val = v
        self.update()

    def set_value(self, v):
        self._anim.setStartValue(self._val)
        self._anim.setEndValue(float(v))
        self._anim.start()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h_w = self.width(), self.height()
        r = 78
        cx, cy = w // 2, 100

        # Progress ratio
        ratio = max(0, min(1, self._val / self._max))
        arc_color = (SUCCESS if ratio < 0.60 else
                     WARNING if ratio < 0.82 else DANGER)

        # Background track
        pen = QPen(QColor(BORDER), 10, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen); p.setBrush(Qt.NoBrush)
        p.drawArc(cx-r, cy-r, r*2, r*2, 225*16, -270*16)

        # Colored arc
        pen.setColor(QColor(arc_color))
        p.setPen(pen)
        p.drawArc(cx-r, cy-r, r*2, r*2, 225*16, -int(270*ratio*16))

        # Center dot
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(arc_color))
        p.drawEllipse(cx-5, cy-5, 10, 10)

        # Value text
        p.setPen(QColor(TEXT_PRI))
        p.setFont(QFont("Segoe UI", 22, QFont.Bold))
        p.drawText(QRectF(cx-55, cy-22, 110, 38), Qt.AlignCenter, f"{self._val:.1f}")

        # Unit text
        p.setPen(QColor(TEXT_SEC))
        p.setFont(QFont("Segoe UI", 10))
        p.drawText(QRectF(cx-40, cy+14, 80, 18), Qt.AlignCenter, self._unit)

        # Icon + title centrados en la parte inferior
        icon_sz  = 20
        text_w   = 108
        block_w  = icon_sz + 6 + text_w          # 134 px total
        start_x  = cx - block_w // 2             # centrado
        p.drawPixmap(int(start_x), 181, self._icon_px)
        p.setPen(QColor(TEXT_SEC))
        p.setFont(QFont("Segoe UI", 10))
        p.drawText(QRectF(start_x + icon_sz + 6, 181, text_w, 20),
                   Qt.AlignLeft | Qt.AlignVCenter, self._title)


# ── KPICard ───────────────────────────────────────────────────────────────────
class KPICard(QFrame):
    def __init__(self, title, value, unit, color, icon_name, fmt="{:.0f}", trend=2.3,
                 history=None, parent=None):
        super().__init__(parent)
        self._fmt = fmt
        self._counter = 0.0
        self._color = color
        self.setFixedHeight(130)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(f"""
            QFrame {{
                background:{BG_CARD}; border:1px solid {BORDER}; border-radius:12px;
            }}
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20); shadow.setColor(QColor(0,0,0,80)); shadow.setOffset(0,4)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 10)
        layout.setSpacing(4)

        # Top row: icon badge + trend
        top = QHBoxLayout(); top.setSpacing(8)
        # Badge: usamos QFrame contenedor para que el stylesheet no pise el pixmap
        icon_badge = QFrame()
        icon_badge.setFixedSize(42, 42)
        icon_badge.setStyleSheet(f"""
            QFrame {{
                background:{color}22; border-radius:9px; border:1px solid {color}55;
            }}
        """)
        badge_inner = QVBoxLayout(icon_badge)
        badge_inner.setContentsMargins(0, 0, 0, 0)
        badge_icon = QLabel()
        badge_icon.setAlignment(Qt.AlignCenter)
        badge_icon.setPixmap(_pixmap(icon_name, 26))
        badge_inner.addWidget(badge_icon)
        trend_lbl = QLabel(f"{'▲' if trend >= 0 else '▼'} {abs(trend):.1f}%")
        trend_lbl.setStyleSheet(f"""
            color:{'#00E096' if trend >= 0 else '#FF4747'};
            font-size:11px; font-weight:700;
            background:{'#00E09622' if trend >= 0 else '#FF474722'};
            border-radius:4px; padding:2px 6px;
        """)
        top.addWidget(icon_badge)
        top.addStretch()
        top.addWidget(trend_lbl)
        layout.addLayout(top)

        # Value + unit
        val_row = QHBoxLayout(); val_row.setSpacing(4)
        self._val_lbl = QLabel(fmt.format(value))
        self._val_lbl.setStyleSheet(f"color:{TEXT_PRI}; font-size:26px; font-weight:700;")
        unit_lbl = QLabel(unit)
        unit_lbl.setStyleSheet(f"color:{TEXT_SEC}; font-size:12px; padding-top:10px;")
        val_row.addWidget(self._val_lbl)
        val_row.addWidget(unit_lbl)
        val_row.addStretch()
        layout.addLayout(val_row)

        # Title
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color:{TEXT_SEC}; font-size:11px;")
        layout.addWidget(title_lbl)

        # Sparkline
        h = history or [value * (0.9 + random.random()*0.2) for _ in range(18)]
        self._spark = Sparkline(h, color)
        layout.addWidget(self._spark)

        # Animated counter
        self._anim = QPropertyAnimation(self, b"counter_val")
        self._anim.setDuration(1300); self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.setStartValue(0.0); self._anim.setEndValue(float(value))
        self._anim.start()

    @pyqtProperty(float)
    def counter_val(self):
        return self._counter

    @counter_val.setter
    def counter_val(self, v):
        self._counter = v
        self._val_lbl.setText(self._fmt.format(v))

    def update_value(self, value, new_history=None):
        self._anim.setStartValue(self._counter)
        self._anim.setEndValue(float(value))
        self._anim.start()
        if new_history:
            self._spark.set_data(new_history)


# ── BarChartWidget ────────────────────────────────────────────────────────────
class BarChartWidget(QWidget):
    def __init__(self, data, labels, title="", color=ACCENT, parent=None):
        super().__init__(parent)
        self._data = data; self._labels = labels
        self._title = title; self._color = QColor(color)
        self._progress = 0.0
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._anim = QPropertyAnimation(self, b"anim_progress")
        self._anim.setDuration(900); self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.setStartValue(0.0); self._anim.setEndValue(1.0)

    @pyqtProperty(float)
    def anim_progress(self):
        return self._progress

    @anim_progress.setter
    def anim_progress(self, v):
        self._progress = v
        self.update()

    def start_animation(self):
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()

    def set_data(self, data, labels):
        self._data = data; self._labels = labels
        self.update()

    def paintEvent(self, event):
        if not self._data: return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        pl, pr, pt, pb = 44, 12, 28, 28
        cw = w - pl - pr; ch = h - pt - pb
        n = len(self._data); mx = max(self._data) or 1

        # Title
        if self._title:
            p.setPen(QColor(TEXT_SEC))
            p.setFont(QFont("Segoe UI", 10, QFont.Bold))
            p.drawText(QRectF(pl, 4, cw, 18), Qt.AlignLeft | Qt.AlignVCenter, self._title)

        # Grid
        p.setPen(QPen(QColor(BORDER), 1, Qt.DashLine))
        for i in range(5):
            y = pt + ch * i / 4
            p.drawLine(pl, int(y), pl+cw, int(y))
            p.setPen(QColor(TEXT_SEC)); p.setFont(QFont("Segoe UI", 7))
            p.drawText(QRectF(0, y-8, pl-4, 16), Qt.AlignRight|Qt.AlignVCenter,
                       f"{mx*(1-i/4):.0f}")
            p.setPen(QPen(QColor(BORDER), 1, Qt.DashLine))

        # Bars
        slot = cw / n; bw = slot * 0.55; gap = (slot - bw) / 2
        for i, val in enumerate(self._data):
            bh = (val / mx) * ch * self._progress
            x = pl + i * slot + gap
            y = pt + ch - bh

            grad = QLinearGradient(0, y, 0, y + bh)
            c = self._color
            lt = QColor(min(255,c.red()+50), min(255,c.green()+50), min(255,c.blue()+50))
            grad.setColorAt(0, lt); grad.setColorAt(1, c)
            p.setBrush(grad); p.setPen(Qt.NoPen)
            p.drawRoundedRect(QRectF(x, y, bw, bh), 3, 3)

            p.setPen(QColor(TEXT_SEC)); p.setFont(QFont("Segoe UI", 8))
            p.drawText(QRectF(x-4, h-pb, bw+8, pb), Qt.AlignCenter, self._labels[i])

            if self._progress > 0.6:
                p.setPen(QColor(TEXT_PRI)); p.setFont(QFont("Segoe UI", 8, QFont.Bold))
                p.drawText(QRectF(x-4, y-16, bw+8, 14), Qt.AlignCenter, str(val))


# ── AlarmRow ──────────────────────────────────────────────────────────────────
ALARM_COLORS = {"CRÍTICA": DANGER, "ADVERTENCIA": WARNING, "INFO": ACCENT}

class AlarmRow(QFrame):
    def __init__(self, severity, timestamp, source, message, parent=None):
        super().__init__(parent)
        self.severity = severity
        self._acked = False
        color = ALARM_COLORS.get(severity, TEXT_SEC)
        self.setStyleSheet(f"""
            QFrame {{
                background:{BG_CARD}; border-left:3px solid {color};
                border-radius:6px; margin:2px 0;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(56)

        row = QHBoxLayout(self)
        row.setContentsMargins(14, 8, 14, 8)
        row.setSpacing(12)

        dot = QLabel("●")
        dot.setStyleSheet(f"color:{color}; font-size:10px;")
        dot.setFixedWidth(10)

        info = QVBoxLayout(); info.setSpacing(1)
        src_lbl = QLabel(f"{source}  ·  {timestamp}")
        src_lbl.setStyleSheet(f"color:{TEXT_SEC}; font-size:10px;")
        msg_lbl = QLabel(message)
        msg_lbl.setStyleSheet(f"color:{TEXT_PRI}; font-size:12px; font-weight:500;")
        info.addWidget(src_lbl); info.addWidget(msg_lbl)

        sev_badge = QLabel(severity)
        sev_badge.setFixedWidth(88)
        sev_badge.setAlignment(Qt.AlignCenter)
        sev_badge.setStyleSheet(f"""
            color:{color}; background:{color}22; border-radius:4px;
            font-size:10px; font-weight:700; padding:2px 6px;
        """)

        self._ack_btn = GlowButton("Confirmar", color="#4A5568")
        self._ack_btn.setFixedSize(90, 26)
        self._ack_btn.clicked.connect(self._acknowledge)

        row.addWidget(dot)
        row.addLayout(info, 1)
        row.addWidget(sev_badge)
        row.addWidget(self._ack_btn)

    def _acknowledge(self):
        self._acked = True
        self.setStyleSheet(f"""
            QFrame {{
                background:{BG_CARD}; border-left:3px solid {TEXT_SEC};
                border-radius:6px; margin:2px 0; opacity:0.5;
            }}
        """)
        self._ack_btn.setEnabled(False)
        self._ack_btn.setText("✓ Confirmado")


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINAS
# ══════════════════════════════════════════════════════════════════════════════

class DashboardPage(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self._d = data
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        # KPI cards
        kpi_row = QHBoxLayout(); kpi_row.setSpacing(12)
        self.kpi_prod = KPICard("Producción / hora", data["production"], "uds",
                                ACCENT, "kpi_production", trend=+3.2,
                                history=data["prod_hist"])
        self.kpi_eff  = KPICard("Eficiencia",  data["efficiency"], "%",
                                SUCCESS, "kpi_efficiency", fmt="{:.1f}", trend=+1.1,
                                history=data["eff_hist"])
        self.kpi_ener = KPICard("Consumo",  data["energy"], "kWh",
                                WARNING, "kpi_energy", fmt="{:.1f}", trend=-2.4,
                                history=data["ener_hist"])
        self.kpi_qual = KPICard("Calidad",   data["quality"], "%",
                                PURPLE, "kpi_quality", fmt="{:.1f}", trend=+0.5,
                                history=data["qual_hist"])
        for c in (self.kpi_prod, self.kpi_eff, self.kpi_ener, self.kpi_qual):
            kpi_row.addWidget(c)
        layout.addLayout(kpi_row)

        # Gauges + large sparkline
        bottom = QHBoxLayout(); bottom.setSpacing(12)

        gauge_frame = QFrame()
        gauge_frame.setStyleSheet(f"background:{BG_CARD}; border:1px solid {BORDER}; border-radius:12px;")
        gf_layout = QHBoxLayout(gauge_frame)
        gf_layout.setContentsMargins(16, 10, 16, 10)
        self.gauge_temp  = CircularGauge("Temperatura", data["temperature"], 120, "°C", "ico_temp", DANGER)
        self.gauge_press = CircularGauge("Presión",     data["pressure"],    10,  "bar", "ico_pressure", ACCENT)
        self.gauge_flow  = CircularGauge("Caudal",      data["flow"],        50,  "m³/h","ico_flow", SUCCESS)
        for g in (self.gauge_temp, self.gauge_press, self.gauge_flow):
            gf_layout.addWidget(g)

        spark_frame = QFrame()
        spark_frame.setStyleSheet(f"background:{BG_CARD}; border:1px solid {BORDER}; border-radius:12px;")
        sf_layout = QVBoxLayout(spark_frame)
        sf_layout.setContentsMargins(16, 12, 16, 12); sf_layout.setSpacing(6)
        lbl = QLabel("Tendencia de producción")
        lbl.setStyleSheet(f"color:{TEXT_SEC}; font-size:11px; font-weight:700; letter-spacing:1px;")
        self.big_spark = Sparkline(data["prod_hist"], ACCENT, show_axes=True)
        sf_layout.addWidget(lbl)
        sf_layout.addWidget(self.big_spark, 1)

        bottom.addWidget(gauge_frame)
        bottom.addWidget(spark_frame, 1)
        layout.addLayout(bottom, 1)

    def refresh(self, data):
        self.kpi_prod.update_value(data["production"], data["prod_hist"])
        self.kpi_eff.update_value(data["efficiency"],  data["eff_hist"])
        self.kpi_ener.update_value(data["energy"],     data["ener_hist"])
        self.kpi_qual.update_value(data["quality"],    data["qual_hist"])
        self.gauge_temp.set_value(data["temperature"])
        self.gauge_press.set_value(data["pressure"])
        self.gauge_flow.set_value(data["flow"])
        self.big_spark.set_data(data["prod_hist"])


class ControlPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        header_lbl = QLabel("Control de Maquinaria")
        header_lbl.setStyleSheet(f"color:{TEXT_PRI}; font-size:16px; font-weight:700;")
        layout.addWidget(header_lbl)

        machines_row = QHBoxLayout(); machines_row.setSpacing(14)
        self.machines = []
        specs = [
            ("Línea 1 — Motor A", True,  74, 82, ACCENT),
            ("Línea 2 — Bomba B", False, 45, 68, SUCCESS),
            ("Línea 3 — Compr. C", True, 91, 95, WARNING),
        ]
        for name, on, speed, temp, color in specs:
            card = self._machine_card(name, on, speed, temp, color)
            machines_row.addWidget(card)
            self.machines.append(card)
        layout.addLayout(machines_row)
        layout.addStretch()

    def _machine_card(self, name, on, speed, temp, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background:{BG_CARD}; border:1px solid {BORDER};
                border-top:3px solid {color}; border-radius:12px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(16); shadow.setColor(QColor(0,0,0,80)); shadow.setOffset(0,4)
        card.setGraphicsEffect(shadow)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 16, 18, 18); lay.setSpacing(12)

        # Header
        hdr = QHBoxLayout()
        led = LEDIndicator(SUCCESS if on else DANGER)
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f"color:{TEXT_PRI}; font-size:13px; font-weight:700;")
        status_lbl = QLabel("OPERATIVO" if on else "DETENIDO")
        status_lbl.setStyleSheet(f"""
            color:{'#00E096' if on else '#FF4747'};
            font-size:10px; font-weight:700;
            background:{'#00E09622' if on else '#FF474722'};
            border-radius:4px; padding:2px 8px;
        """)
        hdr.addWidget(led); hdr.addSpacing(6); hdr.addWidget(name_lbl); hdr.addStretch()
        hdr.addWidget(status_lbl)
        lay.addLayout(hdr)
        lay.addWidget(Divider())

        # Power toggle
        tog_row = QHBoxLayout()
        tog_lbl = QLabel("Encendido")
        tog_lbl.setStyleSheet(f"color:{TEXT_SEC}; font-size:12px;")
        tog = ToggleSwitch(checked=on)

        def _on_toggle(checked, _led=led, _sl=status_lbl, _t=tog):
            _led.set_state(checked, SUCCESS if checked else DANGER)
            _sl.setText("OPERATIVO" if checked else "DETENIDO")
            _sl.setStyleSheet(f"""
                color:{'#00E096' if checked else '#FF4747'};
                font-size:10px; font-weight:700;
                background:{'#00E09622' if checked else '#FF474722'};
                border-radius:4px; padding:2px 8px;
            """)
        tog.toggled.connect(_on_toggle)
        tog_row.addWidget(tog_lbl); tog_row.addStretch(); tog_row.addWidget(tog)
        lay.addLayout(tog_row)

        # Speed slider
        lay.addLayout(self._slider_row("Velocidad", speed, 0, 100, "%", color))
        # Temp slider
        lay.addLayout(self._slider_row("Temp. objetivo", temp, 40, 130, "°C", DANGER))

        # Live readings
        readings = QHBoxLayout(); readings.setSpacing(8)
        for label, val, unit in [("RPM", random.randint(800,3200), ""), ("kW", round(random.uniform(4,22),1), "")]:
            chip = QFrame()
            chip.setStyleSheet(f"background:{BG_PANEL}; border-radius:6px; border:1px solid {BORDER};")
            ch_lay = QVBoxLayout(chip); ch_lay.setContentsMargins(10, 6, 10, 6); ch_lay.setSpacing(0)
            v_lbl = QLabel(f"{val}{unit}")
            v_lbl.setStyleSheet(f"color:{color}; font-size:14px; font-weight:700;")
            l_lbl = QLabel(label)
            l_lbl.setStyleSheet(f"color:{TEXT_SEC}; font-size:10px;")
            ch_lay.addWidget(v_lbl); ch_lay.addWidget(l_lbl)
            readings.addWidget(chip, 1)
        lay.addLayout(readings)

        return card

    def _slider_row(self, label, value, mn, mx, unit, color):
        row = QHBoxLayout(); row.setSpacing(8)
        lbl = QLabel(label); lbl.setStyleSheet(f"color:{TEXT_SEC}; font-size:11px;"); lbl.setFixedWidth(100)
        sl = QSlider(Qt.Horizontal); sl.setRange(mn, mx); sl.setValue(value); sl.setCursor(Qt.PointingHandCursor)
        sl.setStyleSheet(f"""
            QSlider::groove:horizontal {{ height:4px; background:{BG_PANEL}; border-radius:2px; }}
            QSlider::sub-page:horizontal {{ background:{color}; border-radius:2px; }}
            QSlider::handle:horizontal {{
                background:{color}; border:2px solid {BG_CARD};
                width:14px; height:14px; margin:-6px 0; border-radius:7px;
            }}
        """)
        val_lbl = QLabel(f"{value}{unit}"); val_lbl.setFixedWidth(38)
        val_lbl.setStyleSheet(f"color:{color}; font-size:11px; font-weight:700;")
        sl.valueChanged.connect(lambda v, vl=val_lbl, u=unit: vl.setText(f"{v}{u}"))
        row.addWidget(lbl); row.addWidget(sl, 1); row.addWidget(val_lbl)
        return row


class AnalyticsPage(QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self._d = data
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        header_lbl = QLabel("Análisis de Producción")
        header_lbl.setStyleSheet(f"color:{TEXT_PRI}; font-size:16px; font-weight:700;")
        layout.addWidget(header_lbl)

        charts_row = QHBoxLayout(); charts_row.setSpacing(12)

        # Bar chart: producción por hora
        bar_frame = QFrame()
        bar_frame.setStyleSheet(f"background:{BG_CARD}; border:1px solid {BORDER}; border-radius:12px;")
        bf_lay = QVBoxLayout(bar_frame); bf_lay.setContentsMargins(12, 12, 12, 12)
        self.bar = BarChartWidget(
            data["hourly_prod"], data["hourly_labels"],
            title="UNIDADES PRODUCIDAS POR HORA", color=ACCENT)
        bf_lay.addWidget(self.bar, 1)

        # Line chart: eficiencia 24h
        eff_frame = QFrame()
        eff_frame.setStyleSheet(f"background:{BG_CARD}; border:1px solid {BORDER}; border-radius:12px;")
        ef_lay = QVBoxLayout(eff_frame); ef_lay.setContentsMargins(12, 12, 12, 12); ef_lay.setSpacing(4)
        eff_lbl = QLabel("TENDENCIA DE EFICIENCIA (24 h)")
        eff_lbl.setStyleSheet(f"color:{TEXT_SEC}; font-size:10px; font-weight:700; letter-spacing:1px;")
        self.eff_line = Sparkline(data["eff_hist"], SUCCESS, show_axes=True)
        ef_lay.addWidget(eff_lbl); ef_lay.addWidget(self.eff_line, 1)

        charts_row.addWidget(bar_frame, 1)
        charts_row.addWidget(eff_frame, 1)
        layout.addLayout(charts_row, 1)

    def on_enter(self):
        self.bar.start_animation()

    def refresh(self, data):
        self.bar.set_data(data["hourly_prod"], data["hourly_labels"])
        self.eff_line.set_data(data["eff_hist"])


class AlarmsPage(QWidget):
    ALARMS = [
        ("CRÍTICA",     "14:23:01", "Línea 1 — Motor A",  "Temperatura crítica detectada: 108 °C"),
        ("ADVERTENCIA", "14:20:33", "Línea 2 — Bomba B",  "Presión por debajo del umbral: 2.1 bar"),
        ("CRÍTICA",     "14:18:55", "Compresor C",         "Vibración anómala: 12.4 mm/s"),
        ("INFO",        "14:15:00", "Sistema",             "Mantenimiento preventivo programado en 24 h"),
        ("ADVERTENCIA", "14:10:12", "Sensor S-04",         "Calibración pendiente — desviación 3.2%"),
        ("INFO",        "13:55:40", "Red industrial",      "Actualización de firmware disponible v2.4.1"),
        ("ADVERTENCIA", "13:40:27", "Línea 1 — Cinta",    "Velocidad reducida al 68% — desgaste detectado"),
        ("CRÍTICA",     "13:22:08", "UPS Principal",       "Batería de respaldo al 18% — carga inmediata"),
        ("INFO",        "13:10:00", "Sistema",             "Backup de configuración completado exitosamente"),
        ("ADVERTENCIA", "12:58:33", "Válvula V-12",        "Tiempo de respuesta elevado: 340 ms"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # Header + stats
        hdr = QHBoxLayout()
        title = QLabel("Centro de Alarmas")
        title.setStyleSheet(f"color:{TEXT_PRI}; font-size:16px; font-weight:700;")
        self._stats = QLabel(self._stats_text())
        self._stats.setStyleSheet(f"color:{TEXT_SEC}; font-size:11px;")
        hdr.addWidget(title); hdr.addStretch(); hdr.addWidget(self._stats)
        layout.addLayout(hdr)

        # Filter buttons
        frow = QHBoxLayout(); frow.setSpacing(8)
        self._filters = {}
        for label, color in [("Todas", TEXT_PRI), ("CRÍTICA", DANGER),
                              ("ADVERTENCIA", WARNING), ("INFO", ACCENT)]:
            btn = FilterButton(label, color)
            btn.clicked.connect(lambda _, l=label: self._apply_filter(l))
            self._filters[label] = btn
            frow.addWidget(btn)
        self._filters["Todas"].setChecked(True)
        frow.addStretch()
        ack_all = GlowButton("Confirmar todas", color="#4A5568")
        ack_all.setFixedHeight(30)
        ack_all.clicked.connect(self._ack_all)
        frow.addWidget(ack_all)
        layout.addLayout(frow)

        # Scroll area
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border:none; background:transparent; }}
            QScrollBar:vertical {{ background:{BG_PANEL}; width:6px; border-radius:3px; }}
            QScrollBar::handle:vertical {{ background:{BORDER}; border-radius:3px; min-height:20px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
        """)
        inner = QWidget(); inner.setStyleSheet("background:transparent;")
        self._alarm_layout = QVBoxLayout(inner)
        self._alarm_layout.setContentsMargins(0, 0, 0, 0)
        self._alarm_layout.setSpacing(4)

        self._rows = []
        for args in self.ALARMS:
            row = AlarmRow(*args)
            self._alarm_layout.addWidget(row)
            self._rows.append(row)
        self._alarm_layout.addStretch()
        scroll.setWidget(inner)
        layout.addWidget(scroll, 1)

    def _stats_text(self):
        c = sum(1 for a in self.ALARMS if a[0] == "CRÍTICA")
        w = sum(1 for a in self.ALARMS if a[0] == "ADVERTENCIA")
        return f"Críticas: {c}  ·  Advertencias: {w}  ·  Total: {len(self.ALARMS)}"

    def _apply_filter(self, label):
        for k, b in self._filters.items():
            b.setChecked(k == label)
        for row in self._rows:
            row.setVisible(label == "Todas" or row.severity == label)

    def _ack_all(self):
        for row in self._rows:
            row._acknowledge()


# ══════════════════════════════════════════════════════════════════════════════
# VENTANA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

class IndustrialDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self._data = self._init_data()
        self._build_ui()

        self._data_timer = QTimer()
        self._data_timer.timeout.connect(self._update_live_data)
        self._data_timer.start(2500)

        self._clock_timer = QTimer()
        self._clock_timer.timeout.connect(self._tick_clock)
        self._clock_timer.start(1000)

    # ── Datos ─────────────────────────────────────────────────────────────────

    def _init_data(self):
        def hist(base, n=24):
            v = base
            h = []
            for _ in range(n):
                v = _rand_walk(v, 0.04, base*0.7, base*1.3)
                h.append(round(v, 1))
            return h

        prod_hist = hist(1200, 24)
        return {
            "production": prod_hist[-1],
            "efficiency": 87.3,
            "energy":     342.5,
            "quality":    96.8,
            "temperature": 72.4,
            "pressure":    4.8,
            "flow":        24.2,
            "prod_hist":   prod_hist,
            "eff_hist":    hist(87, 24),
            "ener_hist":   hist(340, 24),
            "qual_hist":   hist(96, 24),
            "hourly_prod": [random.randint(1100, 1400) for _ in range(8)],
            "hourly_labels": ["07h","08h","09h","10h","11h","12h","13h","14h"],
        }

    def _update_live_data(self):
        d = self._data
        d["production"]  = round(_rand_walk(d["production"],  0.03, 800, 1600))
        d["efficiency"]  = round(_rand_walk(d["efficiency"],  0.02, 60, 100), 1)
        d["energy"]      = round(_rand_walk(d["energy"],      0.02, 200, 500), 1)
        d["quality"]     = round(_rand_walk(d["quality"],     0.01, 85, 100), 1)
        d["temperature"] = round(_rand_walk(d["temperature"], 0.03, 20, 115), 1)
        d["pressure"]    = round(_rand_walk(d["pressure"],    0.03, 1, 9.5),  1)
        d["flow"]        = round(_rand_walk(d["flow"],        0.03, 5, 48),   1)
        for key in ("prod_hist","eff_hist","ener_hist","qual_hist"):
            base_key = key.replace("_hist","")
            metric = {"prod_hist":"production","eff_hist":"efficiency",
                      "ener_hist":"energy","qual_hist":"quality"}[key]
            d[key] = d[key][1:] + [d[metric]]

        self._page_dash.refresh(d)
        self._page_analytics.refresh(d)
        self._update_status_bar()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.setWindowTitle("Sistema de Control Industrial  ·  PyQt5")
        self.setMinimumSize(1100, 680)
        self.resize(1280, 760)
        self.setStyleSheet(f"""
            QWidget {{ background:{BG_BASE}; font-family:'Segoe UI'; }}
            QToolTip {{
                background:{BG_CARD}; color:{TEXT_PRI}; border:1px solid {BORDER};
                border-radius:5px; padding:4px 8px; font-size:12px;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())

        body = QHBoxLayout(); body.setContentsMargins(0,0,0,0); body.setSpacing(0)
        body.addWidget(self._build_sidebar())
        body.addWidget(self._build_content(), 1)
        root.addLayout(body, 1)

        root.addWidget(self._build_statusbar())

    def _build_header(self):
        hdr = QFrame()
        hdr.setFixedHeight(56)
        hdr.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #0F1924, stop:1 {BG_BASE});
                border-bottom:1px solid {BORDER};
            }}
        """)
        row = QHBoxLayout(hdr)
        row.setContentsMargins(20, 0, 20, 0); row.setSpacing(0)

        logo = QLabel(); logo.setPixmap(_pixmap("ico_factory", 30))
        logo.setFixedSize(36, 36); logo.setAlignment(Qt.AlignCenter)

        title = QLabel("SCI — Sistema de Control Industrial")
        title.setStyleSheet(f"color:{TEXT_PRI}; font-size:16px; font-weight:700; margin-left:10px;")

        self._sys_dot = QLabel("●")
        self._sys_dot.setStyleSheet(f"color:{SUCCESS}; font-size:12px;")
        sys_lbl = QLabel("Sistema operativo")
        sys_lbl.setStyleSheet(f"color:{TEXT_SEC}; font-size:12px; margin-left:4px;")

        self._clock_lbl = QLabel()
        self._clock_lbl.setStyleSheet(f"""
            color:{ACCENT}; font-size:13px; font-weight:700;
            background:#0F1924; border:1px solid {BORDER};
            border-radius:6px; padding:4px 12px; margin-left:16px;
        """)
        self._tick_clock()

        row.addWidget(logo); row.addWidget(title); row.addStretch()
        row.addWidget(self._sys_dot); row.addWidget(sys_lbl)
        row.addWidget(self._clock_lbl)
        return hdr

    def _build_sidebar(self):
        side = QFrame()
        side.setFixedWidth(190)
        side.setStyleSheet(f"background:{BG_PANEL}; border-right:1px solid {BORDER};")
        lay = QVBoxLayout(side)
        lay.setContentsMargins(0, 16, 0, 16); lay.setSpacing(2)

        sect = QLabel("NAVEGACIÓN")
        sect.setStyleSheet(f"color:{TEXT_SEC}; font-size:9px; font-weight:700; "
                           f"letter-spacing:1.5px; padding:0 20px 8px 20px;")
        lay.addWidget(sect)

        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)

        pages = [
            ("Dashboard",  "nav_dashboard",  0),
            ("Controles",  "nav_controls",   1),
            ("Analíticas", "nav_analytics",  2),
            ("Alarmas",    "nav_alarms",     3),
        ]
        self._nav_btns = []
        for label, icon, idx in pages:
            btn = NavButton(label, icon)
            self._nav_group.addButton(btn, idx)
            btn.clicked.connect(lambda _, i=idx: self._switch_page(i))
            lay.addWidget(btn)
            self._nav_btns.append(btn)

        self._nav_btns[0].setChecked(True)
        lay.addStretch()

        ver = QLabel("v1.0.0  ·  PyQt5")
        ver.setAlignment(Qt.AlignCenter)
        ver.setStyleSheet(f"color:{TEXT_SEC}; font-size:10px; padding:8px;")
        lay.addWidget(ver)
        return side

    def _build_content(self):
        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background:transparent;")

        self._page_dash      = DashboardPage(self._data)
        self._page_controls  = ControlPage()
        self._page_analytics = AnalyticsPage(self._data)
        self._page_alarms    = AlarmsPage()

        for page in (self._page_dash, self._page_controls,
                     self._page_analytics, self._page_alarms):
            self._stack.addWidget(page)

        return self._stack

    def _build_statusbar(self):
        bar = QFrame()
        bar.setFixedHeight(28)
        bar.setStyleSheet(f"background:{BG_PANEL}; border-top:1px solid {BORDER};")
        row = QHBoxLayout(bar)
        row.setContentsMargins(20, 0, 20, 0); row.setSpacing(24)

        self._sb_prod = self._sb_chip("Prod: —")
        self._sb_eff  = self._sb_chip("Efic: —")
        self._sb_temp = self._sb_chip("Temp: —")
        self._sb_time = self._sb_chip("Uptime: 08:42:17")

        for chip in (self._sb_prod, self._sb_eff, self._sb_temp):
            row.addWidget(chip)
        row.addStretch()
        row.addWidget(self._sb_time)
        self._update_status_bar()
        return bar

    def _sb_chip(self, text, color=TEXT_SEC):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{color}; font-size:11px;")
        return lbl

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _switch_page(self, idx):
        self._stack.setCurrentIndex(idx)
        if idx == 2:
            self._page_analytics.on_enter()

    def _tick_clock(self):
        now = datetime.now()
        self._clock_lbl.setText(now.strftime("%d/%m/%Y  %H:%M:%S"))

    def _update_status_bar(self):
        d = self._data
        self._sb_prod.setText(f"Producción: {d['production']} uds/h")
        self._sb_eff.setText(f"Eficiencia: {d['efficiency']}%")
        c = d["temperature"]
        color = DANGER if c > 90 else (WARNING if c > 75 else SUCCESS)
        self._sb_temp.setStyleSheet(f"color:{color}; font-size:11px;")
        self._sb_temp.setText(f"Temperatura: {c} °C")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = IndustrialDashboard()
    win.show()
    sys.exit(app.exec_())
