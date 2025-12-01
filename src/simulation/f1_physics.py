import math
import random
import numpy as np

class F1CarPhysics:
    def __init__(self):
        # -- Estado del Vehículo --
        self.speed_kmh = 0.0
        self.rpm = 3000.0  # Ralentí alto de F1
        self.gear = 1
        
        # -- Temperaturas (Celsius) --
        # Los frenos de carbono funcionan bien entre 400-800°C
        self.brake_temp_fl = 200.0  
        # Neumáticos operan idealmente entre 90-110°C
        self.tyre_temp_fl = 80.0
        self.tyre_press_fl = 22.0   # PSI
        
        # -- Fuerzas --
        self.g_long = 0.0
        self.g_lat = 0.0
        
        # -- Simulación de Pista --
        self.track_position = 0.0
        self.lap_count = 0
        self.track_length = 5200.0 # 5.2km (tipo Silverstone)
        
        # Para evitar que se quede parado:
        # Definimos tramos de "velocidad objetivo" basados en la posición
        # Usamos ruido Perlin simplificado o senos superpuestos para el trazado
        self.stuck_counter = 0

    def update(self, dt):
        """
        Calcula la física para el siguiente paso de tiempo (dt segundos).
        """
        # --- 1. MODELO DE PISTA (Corrección del bloqueo) ---
        # Generamos un trazado procedural más agresivo
        # Onda lenta = Rectas largas vs Curvas
        # Onda rápida = Chicanes / Cambios de dirección
        sector = self.track_position / 300.0
        curvature = math.sin(sector) + 0.5 * math.cos(sector * 2.5)
        
        # Definimos la velocidad ideal para ese punto del circuito
        # Recta (curvature ~ 0) -> 330 km/h
        # Horquilla (curvature > 1) -> 70 km/h
        target_speed = 340 - (abs(curvature) * 250)
        target_speed = max(60.0, target_speed) # FIX: Nunca permitir objetivo 0
        
        # --- 2. DINÁMICA LONGITUDINAL (Motor y Frenos) ---
        delta_v = target_speed - self.speed_kmh
        
        if delta_v > 0:
            # ACELERACIÓN (Limitada por potencia y drag)
            # F1: 0-200 en 4.5s. Aceleración brutal a baja velocidad, menor a alta.
            power_factor = 12000 / (self.speed_kmh + 50) # Curva de par
            acceleration = power_factor * dt
            
            # Limitar aceleración física realista (aprox 1.5G tracción)
            acceleration = min(acceleration, 18.0 * dt) 
            
            self.speed_kmh += acceleration
            self.g_long = (acceleration / dt) / 9.81 # G positivo
            
        else:
            # FRENADA (Brutalidad aerodinámica + Discos)
            # F1 puede frenar a 5G.
            braking_intensity = abs(delta_v) * 0.15 # Cuanto más lejos de la velocidad ideal, más freno
            deceleration = braking_intensity * dt
            
            # Clamp para no frenar más de lo necesario
            if self.speed_kmh - deceleration < target_speed:
                deceleration = self.speed_kmh - target_speed
                
            self.speed_kmh -= deceleration
            self.g_long = -(deceleration / dt) / 9.81 # G negativo

        # FIX: Evitar el cero absoluto si el target es moverse
        if self.speed_kmh < 1.0 and target_speed > 10:
            self.speed_kmh = 5.0

        # --- 3. FUERZAS LATERALES (Curvas) ---
        # G_Lat = v^2 / r. Simulamos 'r' con la curvatura.
        # Solo hay G lateral si el coche se mueve
        if self.speed_kmh > 10:
            raw_lat_g = (self.speed_kmh / 120.0) ** 2 * curvature
            # Suavizado para que no salte de golpe
            self.g_lat = self.g_lat * 0.8 + raw_lat_g * 0.2
        else:
            self.g_lat = 0.0

        # --- 4. CAJA DE CAMBIOS Y RPM (Sonido) ---
        # Relaciones de cambio simuladas (km/h por cada 1000 RPM aprox)
        gear_ratios = [0, 16, 24, 31, 38, 46, 53, 60, 68] # kmh por 1000rpm (aprox)
        
        # Lógica de cambio automático
        # Subir marcha si RPM > 11800
        # Bajar marcha si RPM < 8000 (y no es 1ª)
        current_ratio_speed = self.speed_kmh / (self.rpm / 1000.0 + 0.001)
        
        ideal_gear = self.gear
        # Buscamos la marcha donde las RPM estén entre 9000 y 12000 para esta velocidad
        for g in range(1, 9):
            test_rpm = self.speed_kmh / (gear_ratios[g] / 1000.0)
            if 6000 < test_rpm < 12500:
                ideal_gear = g
                break
        
        # Retardo en el cambio (simulación de caja seamless)
        self.gear = ideal_gear
        
        # Calcular RPM exactas basado en velocidad y marcha fija
        target_rpm = (self.speed_kmh / gear_ratios[self.gear]) * 1000.0
        target_rpm = max(3000, target_rpm) # Anti-calado
        
        # Añadir ruido y vibración a las RPM
        self.rpm = target_rpm + random.uniform(-50, 50)

# --- 5. TERMODINÁMICA (RE-CALIBRADA) ---
        
        # A) FRENOS: Energía cinética -> Calor
        if self.g_long < -0.1: 
            energy_input = abs(self.g_long) * self.speed_kmh * 1.5 * dt
            self.brake_temp_fl += energy_input
        
        # Enfriamiento de frenos
        cooling_air_flow = 0.05 + (self.speed_kmh * 0.002) 
        temp_diff = self.brake_temp_fl - 25.0 
        self.brake_temp_fl -= temp_diff * cooling_air_flow * dt
        self.brake_temp_fl = max(25.0, self.brake_temp_fl)

        # B) NEUMÁTICOS: Fricción + Transferencia
        # 1. Calor por rodadura y Fricción
        rolling_heat = self.speed_kmh * 0.1 * dt
        scrub_heat = abs(self.g_lat) * 20.0 * dt
        
        # 2. TRANSFERENCIA TÉRMICA DE FRENOS (RIM SOAK)
        # CORRECCIÓN: Reducimos drásticamente el factor de 0.002 a 0.0001
        # El calor tarda mucho en pasar del disco a la goma (aire aislante)
        rim_soak = 0.0
        if self.brake_temp_fl > 300:
            rim_soak = (self.brake_temp_fl - 300) * 0.00015 * dt # Factor reducido x10
        
        total_heat_in = rolling_heat + scrub_heat + rim_soak
        
        # Enfriamiento neumático
        tyre_cooling = (self.tyre_temp_fl - 25.0) * (0.05 + self.speed_kmh * 0.001) * dt
        self.tyre_temp_fl += total_heat_in - tyre_cooling
        self.tyre_temp_fl = max(25.0, self.tyre_temp_fl)
        
        # C) PRESIÓN (Ley de Gases Ideales - Calibrada)
        # Base: 22.0 PSI a 100°C.
        # Sensibilidad: 0.05 PSI por grado (aprox F1 standard)
        base_temp = 100.0
        base_psi = 22.0
        psi_per_deg = 0.05 # Reducido de 0.1 a 0.05 para ser más estable
        
        delta_t = self.tyre_temp_fl - base_temp
        self.tyre_press_fl = base_psi + (delta_t * psi_per_deg)


        # --- 6. POSICIÓN ---
        dist_m = (self.speed_kmh / 3.6) * dt
        self.track_position += dist_m
        if self.track_position > self.track_length:
            self.track_position = 0
            self.lap_count += 1

    def get_state(self):
        return {
            "speed": self.speed_kmh,
            "rpm": self.rpm,
            "brake_temp_fl": self.brake_temp_fl,
            "tyre_temp_fl": self.tyre_temp_fl,
            "tyre_pressure_fl": self.tyre_press_fl,
            "g_lat": self.g_lat,    # Añadido para debug
            "g_long": self.g_long   # Añadido para debug
        }