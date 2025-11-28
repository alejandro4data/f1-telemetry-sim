# ⚡ Electronics & DAQ (Data Acquisition)

## 1. The Signal Chain (Cadena de Señal)
1.  **Transducer (Sensor):** Convierte física (Temp/Presión) en voltaje.
2.  **ADC (Analog-to-Digital Converter):** Convierte voltaje en bits.
    *   **Resolution:** Número de bits (ej. 12-bit = 4096 pasos).
    *   **Quantization Error:** La pérdida de precisión al digitalizar.

## 2. Sampling (Muestreo)
*   **Sample Rate (Frecuencia):** Cuántas veces por segundo leemos el sensor (medido en **Hz**).
*   **Aliasing:** Error visual cuando muestreas mas lento que la vibración real (la rueda parece girar al revés en TV).
*   **Nyquist Theorem:** Debes muestrear al menos al doble de la frecuencia de la señal que quieres medir.

## 3. CAN Bus (Controller Area Network)
El estándar de comunicación en automoción.
*   **Node:** Cualquier dispositivo conectado (ECU, Sensor, Dash).
*   **Bus Load:** Porcentaje de saturación de la red. Si pasa del 80%, hay riesgo de **Packet Loss** (Pérdida de datos).
*   **Arbitration ID:** Identificador del mensaje. Define la **Priority** (Prioridad). ID más bajo = Prioridad más alta.
*   **Payload:** Los datos útiles dentro del mensaje (máx 8 bytes en CAN 2.0).
*   **Little Endian / Big Endian:** El orden de los bytes. En F1 se suele usar **Big Endian** (Motorola convention).

## 4. Telemetry Channels (Canales de Telemetría)
Nombres estándar de variables en software de F1 (como McLaren ATLAS o MoTeC):
*   `vCar`: Vehicle Speed.
*   `nEngine`: Engine RPM.
*   `pBrakeF`: Brake Pressure Front.
*   `tTyreFL`: Tyre Temperature Front Left.
*   `aLat`: Lateral Acceleration (G).
*   `aLong`: Longitudinal Acceleration (G).