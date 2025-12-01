import can
import struct
import json
import time
import pandas as pd
from collections import deque
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config" / "sensors.json"

class TelemetryReceiver:
    def __init__(self, channel='224.0.0.1', bustype='udp_multicast', buffer_size=100):
        """
        Inicializa el receptor de telemetría.
        :param buffer_size: Cuántos puntos de datos guardamos para las gráficas (Rolling Window).
        """
        self.channel = channel
        self.bustype = bustype
        self.bus = None
        self.running = False
        
        # Cargar diccionario de IDs (DBC)
        with open(CONFIG_PATH, "r") as f:
            self.sensor_config = json.load(f)
        
        # Crear mapa inverso: ID -> Nombre del Sensor (ej. 512 -> 'brake_temp_fl')
        self.id_map = {v['id']: k for k, v in self.sensor_config.items()}
        
        # Buffer de datos: Un diccionario de listas (deques)
        # Estructura: {'speed': [100, 101, ...], 'rpm': [4000, 4100, ...]}
        self.data_buffer = {key: deque(maxlen=buffer_size) for key in self.sensor_config.keys()}
        self.timestamps = deque(maxlen=buffer_size)

    def connect(self):
        try:
            self.bus = can.interface.Bus(channel=self.channel, bustype=self.bustype)
            print(f"✅ [Telemetry] Connected to {self.channel}")
        except Exception as e:
            print(f"❌ [Telemetry] Connection Failed: {e}")

    def fetch_latest_data(self):
        """
        Lee todos los mensajes pendientes en el bus (Polling).
        Se llama desde el bucle principal de la interfaz gráfica.
        """
        if not self.bus:
            return

        # Leemos hasta vaciar la cola del bus para no tener lag
        while True:
            msg = self.bus.recv(timeout=0.0) # Non-blocking
            if msg is None:
                break # No hay más mensajes
            
            # Decodificar
            if msg.arbitration_id in self.id_map:
                sensor_name = self.id_map[msg.arbitration_id]
                fmt = self.sensor_config[sensor_name]['format']
                
                try:
                    # Unpack: Bytes -> Float
                    value = struct.unpack(fmt, msg.data)[0]
                    
                    # Guardar en el buffer
                    self.data_buffer[sensor_name].append(value)
                    
                    # Solo añadimos timestamp una vez por ciclo (hack simple)
                    if sensor_name == "speed": 
                        self.timestamps.append(time.time())
                        
                except struct.error:
                    print(f"⚠️ Error decoding ID {msg.arbitration_id}")

    def get_dataframe(self):
        """
        Devuelve los datos actuales como un Pandas DataFrame.
        CORREGIDO: Sincroniza las longitudes de los arrays para evitar errores.
        """
        # 1. Convertimos los deques a listas normales
        data = {k: list(v) for k, v in self.data_buffer.items()}
        
        # 2. Si no hay datos, devolvemos DataFrame vacío
        if not data:
            return pd.DataFrame()

        # 3. Encontramos la longitud mínima entre todos los sensores
        # (Ej: Si speed tiene 100 datos y rpm tiene 99, min_len es 99)
        min_len = min(len(v) for v in data.values())
        
        # 4. Recortamos todas las listas para que tengan esa longitud exacta
        # Cogemos los ÚLTIMOS 'min_len' datos (los más recientes)
        clean_data = {}
        for key, values in data.items():
            if min_len > 0:
                clean_data[key] = values[-min_len:] 
            else:
                clean_data[key] = []
        
        return pd.DataFrame(clean_data)