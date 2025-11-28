# 🏎️ Vehicle Dynamics (Dinámica Vehicular)

## 1. 6DOF: Six Degrees of Freedom (6 Grados de Libertad)
En simulación, definimos el movimiento del coche en el espacio 3D usando 6 ejes.

### Translation (Traslación - Movimiento lineal)
1.  **Longitudinal (Surge):** Movimiento adelante/atrás (Aceleración/Frenada).
2.  **Lateral (Sway):** Movimiento izquierda/derecha.
3.  **Vertical (Heave):** Movimiento arriba/abajo (Suspensión/Baches).

### Rotation (Rotación - Movimiento angular)
4.  **Roll (Alabeo):** Rotación sobre el eje longitudinal. El coche se "inclina" en las curvas.
5.  **Pitch (Cabeceo):** Rotación sobre el eje lateral.
    *   **Dive:** El morro baja al frenar.
    *   **Squat:** El morro sube al acelerar.
6.  **Yaw (Guiñada):** Rotación sobre el eje vertical. Es el giro que controlas con el volante (**Steering**).

---

## 2. Load Transfer (Transferencia de Carga)
Concepto crítico para la física de frenado.

### The Concept (El Concepto)
El peso total (**Mass**) no cambia, pero la fuerza vertical sobre cada rueda (**Vertical Load**) varía dinámicamente según la aceleración.

### Longitudinal Load Transfer
Al frenar (**Braking**), la carga se desplaza al eje delantero (**Front Axle**).
*   **Front Tyres:** Ganan carga -> Ganan agarre (**Grip**).
*   **Rear Tyres:** Pierden carga -> Pierden agarre.
    *   *Riesgo:* **Rear Locking** (Bloqueo de ruedas traseras) -> **Oversteer** (Sobreviraje/Trompo).

### Lateral Load Transfer
Al girar (**Cornering**), la carga se desplaza a las ruedas exteriores.
*   **Body Roll:** La carrocería se inclina. La suspensión debe controlar esto con las **Anti-Roll Bars**.

---

## 3. Aerodynamics (Aerodinámica)

### Drag (Resistencia al avance)
La fuerza del aire que empuja el coche hacia atrás.
*   Crece con el cuadrado de la velocidad ($V^2$).
*   Afecta a la **Top Speed** (Velocidad punta).

### Downforce (Carga Aerodinámica)
La fuerza del aire que empuja el coche hacia el suelo (Grip vertical gratis).
*   Aumenta la capacidad de paso por curva (**Cornering Speed**).
*   Depende del **Ride Height** (Altura del coche al suelo).

### Center of Pressure (CoP)
El punto geométrico donde se aplica la fuerza aerodinámica.
*   **Aero Balance:** La relación entre el agarre delantero y trasero.
    *   Si CoP está muy adelante -> **Oversteer** (El coche gira mucho).
    *   Si CoP está muy atrás -> **Understeer** (El coche no quiere girar).