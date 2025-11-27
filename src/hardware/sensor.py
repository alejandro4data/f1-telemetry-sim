import struct
import json
import time
from pathlib import Path

# Load config once
CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "sensors.json"

with open(CONFIG_PATH, "r") as f:
    SENSOR_MAP = json.load(f)

class VirtualSensor:
    def __init__(self, sensor_key, can_interface):
        """
        :param sensor_key: String key matching config/sensors.json (e.g., 'speed')
        :param can_interface: Instance of CanInterface
        """
        if sensor_key not in SENSOR_MAP:
            raise ValueError(f"Sensor '{sensor_key}' not defined in config.")
            
        self.config = SENSOR_MAP[sensor_key]
        self.can_interface = can_interface
        self.sensor_key = sensor_key
        self.current_value = 0.0

    def send(self, value):
        """
        Encodes the float value into bytes and puts it on the bus.
        """
        self.current_value = float(value)
        
        # PACKING: Convert float -> bytes (Real ECU behavior)
        # using the format specified in JSON (e.g., '>f')
        try:
            payload = struct.pack(self.config['format'], self.current_value)
            
            # Send via CAN Interface
            self.can_interface.send_message(
                arbitration_id=self.config['id'],
                data_bytes=payload
            )
        except Exception as e:
            print(f"Error packing data for {self.sensor_key}: {e}")