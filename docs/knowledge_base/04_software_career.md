# 👨‍💻 Software Engineering in Motorsport

## 1. Key Roles (Roles Clave)
*   **Embedded Engineer:** Programa el firmware del coche (C/C++, Assembly).
*   **Vehicle Dynamics Engineer:** Crea modelos matemáticos (**Physics Models**) en Matlab/Simulink/Python.
*   **Data Engineer:** Analiza los datos de telemetría para encontrar problemas de fiabilidad (**Reliability**) o rendimiento (**Performance**).
*   **Simulator Engineer:** Mantiene el **DiL (Driver-in-the-Loop)** simulator (donde entra tu proyecto).

## 2. Core Concepts (Conceptos Nucleares)

### Real-Time Systems (Sistemas de Tiempo Real)
*   **Hard Real-Time:** El retraso es inaceptable (Fallo catastrófico). Ej: Control del acelerador (**Throttle Map**).
*   **Soft Real-Time:** El retraso degrada la calidad pero no rompe nada. Ej: La pantalla del volante.
*   **Deterministic Latency:** Saber exactamente cuánto tarda una función en ejecutarse (sin sorpresas).

### HIL (Hardware-in-the-Loop)
Técnica de testeo donde conectas una ECU real a un ordenador que simula el coche. La ECU cree que está corriendo en Silverstone, pero está en una mesa de laboratorio.

### Fault Injection (Inyección de Fallos)
Pruebas de software donde provocas errores a propósito para ver si el sistema sobrevive (**Fail-Safe**).
*   *Ejemplo:* Simular que el sensor de temperatura se desconecta (valor `NaN` o `-999`). El software debe activar el **Limp Mode** (Modo degradado) para volver a boxes, no acelerar a fondo.

## 3. Skills for your Project (Habilidades para tu proyecto)
Para que este simulador impresione a un reclutador de F1:
1.  **Asynchronous Programming:** Manejar múltiples sensores a diferentes frecuencias (**Multithreading/AsyncIO**).
2.  **Binary Protocols:** Manejo de `struct` y empaquetado de bits (**Bitwise operations**).
3.  **Physical Correlation:** Que los datos "parezcan" reales.