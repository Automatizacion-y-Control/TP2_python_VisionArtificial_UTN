# Paleta de colores del panel industrial
C = {
    "bg_base":    "#0C1017",
    "bg_panel":   "#131A24",
    "bg_card":    "#1C2533",
    "bg_input":   "#0E1822",
    "bg_deep":    "#080E14",
    "accent":     "#00D4FF",
    "accent_dim": "#007A99",
    "accent_dark":"#003845",
    "success":    "#00E676",
    "warning":    "#FFD600",
    "error":      "#FF4444",
    "text_pri":   "#E8EAF6",
    "text_sec":   "#8899AA",
    "text_dim":   "#4A5A6A",
    "border":     "#2A3A4E",
    "border_hi":  "#3A5068",
    "hover":      "#1E2D3E",
    "pressed":    "#0A1520",
    "rojo_bg":    "#2A0808",
    "verde_bg":   "#082A10",
    "amarillo_bg":"#1E1800",
    "rojo_fg":    "#FF6060",
    "verde_fg":   "#60E680",
    "amarillo_fg":"#E8C040",
}

DARK_QSS = f"""
/* ══════════════════════════════════════════════════════════════════════
   BASE
══════════════════════════════════════════════════════════════════════ */
QMainWindow, QWidget {{
    background-color: {C["bg_base"]};
    color: {C["text_pri"]};
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 12px;
}}
QWidget#w_header {{
    background-color: {C["bg_panel"]};
    border-bottom: 1px solid {C["border"]};
}}
QWidget#w_center_panel {{
    background-color: {C["bg_base"]};
}}
QWidget#w_color_bar {{
    background-color: {C["bg_panel"]};
    border: 1px solid {C["border"]};
    border-radius: 6px;
}}

/* ══════════════════════════════════════════════════════════════════════
   SCROLL AREAS
══════════════════════════════════════════════════════════════════════ */
QScrollArea {{
    border: none;
    background-color: transparent;
}}
QScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}
QScrollBar:vertical {{
    background: {C["bg_panel"]};
    width: 7px;
    border-radius: 3px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {C["border"]};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {C["accent_dim"]};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

/* ══════════════════════════════════════════════════════════════════════
   GROUP BOX
══════════════════════════════════════════════════════════════════════ */
QGroupBox {{
    background-color: {C["bg_panel"]};
    border: 1px solid {C["border"]};
    border-radius: 6px;
    margin-top: 16px;
    padding: 10px 8px 8px 8px;
    font-weight: bold;
    color: {C["accent"]};
    font-size: 10px;
    letter-spacing: 1.5px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    top: 0px;
    padding: 0 5px;
    background-color: {C["bg_panel"]};
}}

/* ══════════════════════════════════════════════════════════════════════
   LABELS
══════════════════════════════════════════════════════════════════════ */
QLabel {{
    color: {C["text_pri"]};
    background-color: transparent;
}}
QLabel#lbl_app_title {{
    font-size: 15px;
    font-weight: bold;
    color: {C["accent"]};
    letter-spacing: 2px;
}}
QLabel#lbl_app_subtitle {{
    font-size: 10px;
    color: {C["text_sec"]};
    letter-spacing: 1px;
}}
QLabel#lbl_section {{
    font-size: 10px;
    font-weight: bold;
    color: {C["text_sec"]};
    letter-spacing: 1.5px;
    padding: 2px 0;
}}
QLabel#lbl_color_big {{
    font-size: 20px;
    font-weight: bold;
    letter-spacing: 4px;
    padding: 4px 12px;
}}
QLabel#lbl_fps_badge {{
    font-size: 11px;
    color: {C["accent"]};
    font-family: "Consolas", monospace;
    padding: 2px 8px;
    border: 1px solid {C["accent_dim"]};
    border-radius: 4px;
    background-color: {C["accent_dark"]};
}}
QLabel#lbl_video_placeholder {{
    color: {C["text_dim"]};
    font-size: 13px;
    qproperty-alignment: AlignCenter;
    background-color: {C["bg_deep"]};
    border: 1px dashed {C["border"]};
    border-radius: 4px;
}}
QLabel#lbl_slider_val {{
    color: {C["accent"]};
    font-family: "Consolas", monospace;
    font-size: 11px;
    min-width: 28px;
    qproperty-alignment: AlignRight;
}}
QLabel#lbl_stat_count {{
    font-size: 20px;
    font-weight: bold;
    font-family: "Consolas", monospace;
    qproperty-alignment: AlignCenter;
}}
QLabel#lbl_stat_label {{
    font-size: 10px;
    color: {C["text_sec"]};
    letter-spacing: 1px;
    qproperty-alignment: AlignCenter;
}}

/* ══════════════════════════════════════════════════════════════════════
   BUTTONS — base
══════════════════════════════════════════════════════════════════════ */
QPushButton {{
    background-color: {C["bg_card"]};
    color: {C["text_pri"]};
    border: 1px solid {C["border"]};
    border-radius: 5px;
    padding: 6px 14px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.5px;
}}
QPushButton:hover {{
    background-color: {C["hover"]};
    border-color: {C["accent_dim"]};
    color: {C["accent"]};
}}
QPushButton:pressed {{
    background-color: {C["pressed"]};
    border-color: {C["accent"]};
}}
QPushButton:disabled {{
    color: {C["text_dim"]};
    background-color: {C["bg_panel"]};
    border-color: {C["border"]};
}}

/* LINK MODE toggle */
QPushButton#btn_link {{
    background-color: {C["bg_card"]};
    color: {C["accent"]};
    border: 2px solid {C["accent_dim"]};
    border-radius: 6px;
    font-size: 12px;
    font-weight: bold;
    padding: 7px 22px;
    letter-spacing: 2px;
    min-width: 140px;
}}
QPushButton#btn_link:hover {{
    background-color: {C["accent_dark"]};
    border-color: {C["accent"]};
}}
QPushButton#btn_link[active="true"] {{
    background-color: {C["accent_dark"]};
    color: {C["accent"]};
    border: 2px solid {C["accent"]};
}}

/* Conectar / Desconectar serial */
QPushButton#btn_connect {{
    background-color: #0A2216;
    color: {C["success"]};
    border: 1px solid #1A4030;
    font-weight: bold;
    letter-spacing: 1px;
    padding: 7px 14px;
}}
QPushButton#btn_connect:hover {{
    background-color: #102C1E;
    border-color: {C["success"]};
}}
QPushButton#btn_connect[connected="true"] {{
    background-color: {C["rojo_bg"]};
    color: {C["error"]};
    border-color: #4A1010;
}}
QPushButton#btn_connect[connected="true"]:hover {{
    background-color: #3A0C0C;
    border-color: {C["error"]};
}}

/* Cámara start/stop */
QPushButton#btn_camera {{
    background-color: #0A1A2A;
    color: {C["accent"]};
    border: 1px solid {C["accent_dim"]};
    font-weight: bold;
    letter-spacing: 1px;
    padding: 7px 14px;
}}
QPushButton#btn_camera:hover {{
    background-color: {C["accent_dark"]};
    border-color: {C["accent"]};
}}
QPushButton#btn_camera[active="true"] {{
    background-color: #3A0808;
    color: {C["error"]};
    border-color: #6A1010;
}}

/* Escanear puertos */
QPushButton#btn_scan {{
    background-color: {C["bg_card"]};
    color: {C["text_sec"]};
    border: 1px solid {C["border"]};
    font-size: 10px;
    padding: 4px 10px;
}}
QPushButton#btn_scan:hover {{
    color: {C["accent"]};
    border-color: {C["accent_dim"]};
}}

/* Botones de color manual */
QPushButton#btn_rojo {{
    background-color: {C["rojo_bg"]};
    color: {C["rojo_fg"]};
    border: 1px solid #5A1010;
    font-weight: bold;
    font-size: 12px;
    letter-spacing: 1.5px;
    padding: 10px;
}}
QPushButton#btn_rojo:hover {{
    background-color: #3A0E0E;
    border-color: {C["error"]};
    color: {C["error"]};
}}
QPushButton#btn_verde {{
    background-color: {C["verde_bg"]};
    color: {C["verde_fg"]};
    border: 1px solid #155A20;
    font-weight: bold;
    font-size: 12px;
    letter-spacing: 1.5px;
    padding: 10px;
}}
QPushButton#btn_verde:hover {{
    background-color: #0C3015;
    border-color: {C["success"]};
    color: {C["success"]};
}}
QPushButton#btn_amarillo {{
    background-color: {C["amarillo_bg"]};
    color: {C["amarillo_fg"]};
    border: 1px solid #4A3800;
    font-weight: bold;
    font-size: 12px;
    letter-spacing: 1.5px;
    padding: 10px;
}}
QPushButton#btn_amarillo:hover {{
    background-color: #282000;
    border-color: {C["warning"]};
    color: {C["warning"]};
}}
QPushButton#btn_ninguno {{
    background-color: #101820;
    color: {C["text_sec"]};
    border: 1px solid {C["border"]};
    font-weight: bold;
    font-size: 12px;
    letter-spacing: 1px;
    padding: 10px;
}}
QPushButton#btn_ninguno:hover {{
    background-color: {C["hover"]};
    color: {C["text_pri"]};
}}

/* Guardar / Cargar / Exportar */
QPushButton#btn_save {{
    background-color: #0A2030;
    color: {C["accent"]};
    border: 1px solid {C["accent_dim"]};
    letter-spacing: 1px;
    padding: 6px 10px;
    font-size: 11px;
}}
QPushButton#btn_save:hover {{ background-color: {C["accent_dark"]}; border-color: {C["accent"]}; }}

QPushButton#btn_load {{
    background-color: {C["bg_card"]};
    color: {C["text_sec"]};
    border: 1px solid {C["border"]};
    letter-spacing: 1px;
    padding: 6px 10px;
    font-size: 11px;
}}
QPushButton#btn_load:hover {{ color: {C["accent"]}; border-color: {C["accent_dim"]}; }}

QPushButton#btn_export {{
    background-color: {C["bg_card"]};
    color: {C["text_sec"]};
    border: 1px solid {C["border"]};
    letter-spacing: 1px;
    padding: 6px 10px;
    font-size: 11px;
}}
QPushButton#btn_export:hover {{ color: {C["warning"]}; border-color: #6A5000; }}

/* ══════════════════════════════════════════════════════════════════════
   COMBOBOX
══════════════════════════════════════════════════════════════════════ */
QComboBox {{
    background-color: {C["bg_input"]};
    color: {C["text_pri"]};
    border: 1px solid {C["border"]};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
    min-height: 24px;
    selection-background-color: {C["accent_dim"]};
}}
QComboBox:hover {{ border-color: {C["accent_dim"]}; }}
QComboBox:focus {{ border-color: {C["accent_dim"]}; }}
QComboBox::drop-down {{
    border: none;
    width: 22px;
    border-left: 1px solid {C["border"]};
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {C["text_sec"]};
    margin-right: 6px;
}}
QComboBox QAbstractItemView {{
    background-color: {C["bg_card"]};
    color: {C["text_pri"]};
    border: 1px solid {C["border"]};
    selection-background-color: {C["accent_dim"]};
    outline: none;
    padding: 2px;
}}

/* ══════════════════════════════════════════════════════════════════════
   MODO LED — control segmentado Pulso / Continuo
══════════════════════════════════════════════════════════════════════ */
QPushButton#btn_led_mode {{
    background-color: {C["bg_card"]};
    color: {C["text_sec"]};
    border: 1px solid {C["border"]};
    border-radius: 4px;
    font-size: 10px;
    font-weight: bold;
    padding: 5px 6px;
    letter-spacing: 0.5px;
}}
QPushButton#btn_led_mode:hover {{
    background-color: {C["hover"]};
    color: {C["text_pri"]};
    border-color: {C["border_hi"]};
}}
QPushButton#btn_led_mode[active="true"] {{
    background-color: {C["accent_dark"]};
    color: {C["accent"]};
    border: 1px solid {C["accent_dim"]};
}}
QPushButton#btn_led_mode[active="true"]:hover {{
    background-color: #004A5C;
    border-color: {C["accent"]};
}}

/* ══════════════════════════════════════════════════════════════════════
   SLIDERS
══════════════════════════════════════════════════════════════════════ */
QSlider::groove:horizontal {{
    height: 4px;
    background: {C["bg_input"]};
    border-radius: 2px;
    border: 1px solid {C["border"]};
}}
QSlider::handle:horizontal {{
    background: {C["accent"]};
    border: 2px solid {C["accent_dark"]};
    width: 13px;
    height: 13px;
    margin: -5px 0;
    border-radius: 7px;
}}
QSlider::sub-page:horizontal {{
    background: {C["accent_dim"]};
    border-radius: 2px;
}}
QSlider::handle:horizontal:hover {{
    background: #50EAFF;
    border-color: {C["accent_dark"]};
}}
QSlider::handle:horizontal:disabled {{
    background: {C["border"]};
}}

/* ══════════════════════════════════════════════════════════════════════
   TABS
══════════════════════════════════════════════════════════════════════ */
QTabWidget::pane {{
    border: 1px solid {C["border"]};
    background-color: {C["bg_panel"]};
    border-radius: 0px 4px 4px 4px;
}}
QTabWidget::tab-bar {{
    alignment: left;
}}
QTabBar::tab {{
    background-color: {C["bg_card"]};
    color: {C["text_dim"]};
    border: 1px solid {C["border"]};
    border-bottom: none;
    padding: 6px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1px;
    min-width: 60px;
}}
QTabBar::tab:selected {{
    background-color: {C["bg_panel"]};
    color: {C["accent"]};
    border-bottom: 2px solid {C["accent"]};
}}
QTabBar::tab:hover:!selected {{
    background-color: {C["hover"]};
    color: {C["text_sec"]};
}}

/* ══════════════════════════════════════════════════════════════════════
   TERMINAL LOG
══════════════════════════════════════════════════════════════════════ */
QPlainTextEdit#log_terminal {{
    background-color: {C["bg_deep"]};
    color: {C["text_sec"]};
    border: 1px solid {C["border"]};
    border-radius: 4px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
    padding: 4px 6px;
    selection-background-color: {C["accent_dim"]};
}}

/* ══════════════════════════════════════════════════════════════════════
   PROGRESS BARS (estadísticas)
══════════════════════════════════════════════════════════════════════ */
QProgressBar {{
    background-color: {C["bg_input"]};
    border: 1px solid {C["border"]};
    border-radius: 3px;
    height: 8px;
    text-align: center;
    color: transparent;
}}
QProgressBar#pb_rojo::chunk    {{ background-color: {C["error"]};   border-radius: 3px; }}
QProgressBar#pb_verde::chunk   {{ background-color: {C["success"]}; border-radius: 3px; }}
QProgressBar#pb_amarillo::chunk {{ background-color: {C["warning"]}; border-radius: 3px; }}

/* ══════════════════════════════════════════════════════════════════════
   SEPARADORES
══════════════════════════════════════════════════════════════════════ */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {C["border"]};
    background-color: {C["border"]};
}}

/* ══════════════════════════════════════════════════════════════════════
   SPLITTER
══════════════════════════════════════════════════════════════════════ */
QSplitter::handle {{
    background-color: {C["border"]};
    width: 2px;
    height: 2px;
}}
QSplitter::handle:hover {{
    background-color: {C["accent_dim"]};
}}
"""

# Colores exportables para uso desde Python (evita duplicar constantes)
ACCENT       = C["accent"]
SUCCESS      = C["success"]
WARNING      = C["warning"]
ERROR        = C["error"]
TEXT_SEC     = C["text_sec"]
BG_BASE      = C["bg_base"]
BG_PANEL     = C["bg_panel"]
BG_CARD      = C["bg_card"]
BORDER       = C["border"]
