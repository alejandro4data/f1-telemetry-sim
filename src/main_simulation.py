import time
import sys
import os

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.hardware.can_interface import CanInterface
from src.hardware.sensor import VirtualSensor
from src.simulation.f1_physics import F1CarPhysics

def main():
    print("--- 🏎️ F1 SIMULATOR ENGINE STARTING ---")
    
    # 1. Initialize Hardware (CAN Bus)
    try:
        can_bus = CanInterface(channel='test_bus', interface='virtual')
        can_bus.connect()
    except Exception as e:
        print(f"CRITICAL: Could not connect to CAN Bus. {e}")
        return

    # 2. Initialize Sensors (Map to config/sensors.json)
    sensors = {
        "speed": VirtualSensor("speed", can_bus),
        "rpm": VirtualSensor("rpm", can_bus),
        "brake_temp_fl": VirtualSensor("brake_temp_fl", can_bus),
        "tyre_temp_fl": VirtualSensor("tyre_temp_fl", can_bus),
        "tyre_pressure_fl": VirtualSensor("tyre_pressure_fl", can_bus)
    }

    # 3. Initialize Physics Engine
    car = F1CarPhysics()
    
    print("--- SYSTEMS GO. TRACKING TELEMETRY ---")
    print("Press CTRL+C to stop.")

    try:
        # Simulation Loop (Running at ~20Hz)
        hz = 20
        dt = 1.0 / hz
        
        while True:
            start_time = time.time()

            # A. Update Physics
            car.update(dt)
            state = car.get_state()

            # B. Read Sensors & Transmit to CAN
            for key, sensor in sensors.items():
                if key in state:
                    sensor.send(state[key])

            # C. Log to Console (Optional, just to see it's alive)
            # \r overwrites the line for a cool dashboard effect
            print(f"\rSPEED: {state['speed']:>3.0f} km/h | "
                  f"RPM: {state['rpm']:>5.0f} | "
                  f"BRAKE: {state['brake_temp_fl']:>4.0f}°C | "
                  f"TYRE: {state['tyre_temp_fl']:>3.0f}°C ({state['tyre_pressure_fl']:.1f} psi)", end="")

            # D. Maintain Timing
            elapsed = time.time() - start_time
            sleep_time = max(0, dt - elapsed)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n--- SIMULATION STOPPED ---")
        can_bus.shutdown()

if __name__ == "__main__":
    main()