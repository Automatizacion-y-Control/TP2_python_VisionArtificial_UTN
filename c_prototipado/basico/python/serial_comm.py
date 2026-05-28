# serial_comm.py
"""
Módulo para la gestión del puerto de comunicación serial física.
Implementa una interfaz tolerante a fallos que cae automáticamente
en modo simulado si el hardware no está disponible.
"""

import sys
import time
from config import SERIAL_PORT, SERIAL_BAUDRATE, SERIAL_PROTOCOL_PHASE, COLOR_METADATA

# Intentar importar pyserial, si no está instalado, forzar modo simulación
try:
    import serial
    import serial.tools.list_ports
    PYSERIAL_AVAILABLE = True
except ImportError:
    PYSERIAL_AVAILABLE = False

class SerialCommunicator:
    def __init__(self):
        self.port = SERIAL_PORT
        self.baudrate = SERIAL_BAUDRATE
        self.phase = SERIAL_PROTOCOL_PHASE
        self.ser = None
        self.is_mock = False

        if not PYSERIAL_AVAILABLE:
            print("\n[ADVERTENCIA] 'pyserial' no está instalado. Iniciando en modo SIMULACIÓN (Mock).")
            self.is_mock = True
            return

        self._connect()

    def _connect(self):
        """Intenta abrir la comunicación serial física con reconexión fallback."""
        try:
            print(f"Intentando conectar al puerto principal: {self.port} a {self.baudrate} bps...")
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            # Pequeña pausa para permitir el reset del microcontrolador al abrir el puerto
            time.sleep(2)
            print(f"[CONECTADO] Puerto {self.port} inicializado con éxito.")
        except serial.SerialException:
            print(f"[FALLA] No se pudo abrir el puerto {self.port}.")
            self._search_and_fallback()

    def _search_and_fallback(self):
        """Busca otros puertos COM disponibles en el sistema para intentar conectar."""
        ports = list(serial.tools.list_ports.comports())
        available_ports = [p.device for p in ports]

        if available_ports:
            print(f"Puertos COM alternativos encontrados: {available_ports}")
            # Intentar conectar con el primer puerto alternativo
            fallback_port = available_ports[0]
            try:
                print(f"Intentando fallback en el puerto: {fallback_port}...")
                self.ser = serial.Serial(fallback_port, self.baudrate, timeout=1)
                self.port = fallback_port
                time.sleep(2)
                print(f"[CONECTADO] Conectado exitosamente al puerto de fallback: {self.port}.")
            except serial.SerialException:
                print(f"[FALLA] Conexión fallida en puerto {fallback_port}.")
                self._activate_mock_mode()
        else:
            print("No se detectaron puertos COM activos en el sistema.")
            self._activate_mock_mode()

    def _activate_mock_mode(self):
        """Activa el modo simulación si no se pudo establecer ninguna conexión serial."""
        self.is_mock = True
        print("=" * 80)
        print("⚠️  MODO SIMULADOR ACTIVO (SERIAL MOCK) ⚠️")
        print("El sistema no detectó ningún microcontrolador físico.")
        print("Las tramas y comandos de salida se imprimirán directamente en la consola.")
        print("=" * 80)

    def send_color(self, color_name):
        """
        Envía la información del color al microcontrolador de acuerdo con la fase activa.
        color_name: 'verde', 'amarillo', 'rojo' o 'ninguno'.
        """
        if color_name not in COLOR_METADATA:
            return

        metadata = COLOR_METADATA[color_name]
        
        if self.phase == 1:
            # Fase 1: Carácter ASCII Único terminado con \n para alineación de búfer
            cmd = metadata["cmd"]
            cmd_str = f"{cmd}\n"
            self._write_raw(cmd_str.encode("ascii"))
            if self.is_mock:
                print(f"[SERIAL SIMULATOR] Enviando Comando Fase 1: '{cmd}' -> LED {metadata['label']}")
        else:
            # Fase 2: Trama Dinámica RGB (Color Global)
            r, g, b = metadata["rgb"]
            self.send_rgb(r, g, b)

    def send_rgb(self, r, g, b):
        """Envía una trama de color dinámico utilizando el delimitador de protocolo de la Fase 2 (Color Global)."""
        trama = f"<A,{r},{g},{b}>\n"
        self._write_raw(trama.encode("ascii"))
        if self.is_mock:
            print(f"[SERIAL SIMULATOR] Enviando Trama Fase 2 (Global RGB): {trama.strip()} -> LED RGB({r}, {g}, {b})")

    def _write_raw(self, byte_data):
        """Escribe los bytes en el puerto serie físico si está conectado."""
        if not self.is_mock and self.ser and self.ser.is_open:
            try:
                self.ser.write(byte_data)
                self.ser.flush()  # Asegurar que se transmitan inmediatamente
            except serial.SerialException as e:
                print(f"\n[ERROR] Pérdida de conexión serial: {e}")
                self._activate_mock_mode()

    def close(self):
        """Cierra el puerto de comunicación de forma limpia al terminar."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"Puerto serial {self.port} cerrado correctamente.")
