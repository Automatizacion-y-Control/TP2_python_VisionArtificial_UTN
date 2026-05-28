import time
from PyQt5.QtCore import QThread, pyqtSignal

try:
    import serial
    import serial.tools.list_ports
    _PYSERIAL = True
except ImportError:
    _PYSERIAL = False


class ConnectThread(QThread):
    """Ejecuta la conexión serial en un hilo separado para no congelar la UI."""
    finished = pyqtSignal(bool, str)

    def __init__(self, communicator: "SerialCommunicator", port: str, baudrate: int, phase: int):
        super().__init__()
        self._comm = communicator
        self._port = port
        self._baudrate = baudrate
        self._phase = phase

    def run(self):
        success, msg = self._comm._do_connect(self._port, self._baudrate, self._phase)
        self.finished.emit(success, msg)


class SerialCommunicator:
    """
    Gestión del puerto serie para el TP2.
    Soporta Fase 1 (char ASCII) y Fase 2 (tramas RGB dinámicas).
    Si pyserial no está disponible, opera en modo SIMULACIÓN (mock).
    """

    def __init__(self):
        self._ser = None
        self.port: str = ""
        self.baudrate: int = 115200
        self.phase: int = 1
        self.is_mock: bool = not _PYSERIAL
        self._connect_thread: ConnectThread | None = None

    # ------------------------------------------------------------------ #
    # Descubrimiento de puertos
    # ------------------------------------------------------------------ #

    @staticmethod
    def get_available_ports() -> list[str]:
        if not _PYSERIAL:
            return []
        return [p.device for p in serial.tools.list_ports.comports()]

    # ------------------------------------------------------------------ #
    # Conexión / desconexión
    # ------------------------------------------------------------------ #

    def connect_async(self, port: str, baudrate: int, phase: int, on_done) -> None:
        """Inicia la conexión en un hilo secundario; llama on_done(success, msg) al terminar."""
        self._connect_thread = ConnectThread(self, port, baudrate, phase)
        self._connect_thread.finished.connect(on_done)
        self._connect_thread.start()

    def _do_connect(self, port: str, baudrate: int, phase: int) -> tuple[bool, str]:
        self.phase = phase
        self.baudrate = baudrate
        if not _PYSERIAL:
            self.is_mock = True
            self.port = "MOCK"
            return True, "pyserial no instalado — modo SIMULACIÓN activo."
        try:
            self._ser = serial.Serial(port, baudrate, timeout=1)
            time.sleep(1.5)          # Tiempo para reset del ESP32
            self.port = port
            self.is_mock = False
            return True, f"Conectado a {port} @ {baudrate} bps — Fase {phase}."
        except serial.SerialException as e:
            self.is_mock = True
            self.port = "MOCK"
            return False, f"No se pudo conectar a {port}: {e} — modo SIMULACIÓN activado."

    def disconnect(self) -> str:
        if self._ser and self._ser.is_open:
            try:
                self._ser.close()
            except Exception:
                pass
        self._ser = None
        self.port = ""
        return "Puerto serie cerrado."

    @property
    def is_connected(self) -> bool:
        if self.is_mock:
            return True
        return self._ser is not None and self._ser.is_open

    # ------------------------------------------------------------------ #
    # Envío de comandos
    # ------------------------------------------------------------------ #

    def send_color(self, color_name: str) -> str:
        """Envía comando según fase activa. Retorna string de log."""
        from config import COLOR_METADATA
        if color_name not in COLOR_METADATA:
            return ""
        meta = COLOR_METADATA[color_name]
        if self.phase == 1:
            payload = f"{meta['cmd']}\n".encode("ascii")
            log_msg = f"Fase 1 → '{meta['cmd']}' ({meta['label']})"
        else:
            r, g, b = meta["rgb"]
            payload = f"<A,{r},{g},{b}>\n".encode("ascii")
            log_msg = f"Fase 2 → <A,{r},{g},{b}> ({meta['label']})"
        self._write(payload)
        return log_msg

    def send_rgb(self, r: int, g: int, b: int) -> str:
        payload = f"<A,{r},{g},{b}>\n".encode("ascii")
        self._write(payload)
        return f"Fase 2 → <A,{r},{g},{b}>"

    def send_pixel(self, index: int, r: int, g: int, b: int) -> str:
        payload = f"<P,{index},{r},{g},{b}>\n".encode("ascii")
        self._write(payload)
        return f"Fase 2 → <P,{index},{r},{g},{b}>"

    def send_brightness(self, value: int) -> str:
        payload = f"<B,{value}>\n".encode("ascii")
        self._write(payload)
        return f"Fase 2 → <B,{value}>"

    def send_off(self) -> str:
        self._write(b"<OFF>\n")
        return "Fase 2 → <OFF>"

    def _write(self, data: bytes) -> None:
        if not self.is_mock and self._ser and self._ser.is_open:
            try:
                self._ser.write(data)
                self._ser.flush()
            except serial.SerialException:
                self.is_mock = True
