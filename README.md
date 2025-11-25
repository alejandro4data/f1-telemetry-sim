# F1 Telemetry & Sensor Simulation Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Protocol](https://img.shields.io/badge/Protocol-CAN%20Bus-orange)
![Status](https://img.shields.io/badge/Status-Development-green)

## 🏎️ Overview

This project simulates a High-Performance Compute environment for motorsport telemetry. It models the physical behavior of a Formula 1 car, generates realistic sensor data, transmits it via a virtual **CAN Bus** network, and visualizes it in real-time.

The goal is to replicate the data pipeline found in professional racing series (F1, WEC, GT3) without requiring physical hardware, serving as a testbed for anomaly detection algorithms and strategy analysis.

## 🚀 Features

- **Advanced Physics Model:** Simulates thermal dynamics (brakes/tyres), rpm, gear ratios, and G-forces based on virtual track inputs.
- **CAN Bus Emulation:** Uses `python-can` to packetize data into binary frames, simulating the actual ECU-to-Telemetry communication protocol.
- **Real-time Dashboard:** Interactive visualization using Streamlit/Dash to monitor vehicle health.
- **Anomaly Detection:** Logic layers to detect punctures, brake overheating, and sensor failures.

## 🛠️ Architecture

The system follows a Producer-Consumer pattern decoupled by a Virtual Network Interface:

1.  **Physics Core (Producer):** Calculates state vectors (Velocity, Temp, Pressure) using rigid body dynamics and thermodynamics.
2.  **Virtual ECU:** Converts physical values into Byte Arrays (Hex) and broadcasts them to a virtual CAN interface (`vcan0`).
3.  **Telemetry Node (Consumer):** Listens to the bus, decodes the binary frames, and pipes data to the analytics engine.

## 📂 Project Structure

```text
├── config/          # Sensor IDs (CAN arbitration) and track parameters
├── src/
│   ├── simulation/  # Physics engine (Math & Logic)
│   ├── hardware/    # Virtual CAN Bus interface & Packet encoding
│   ├── telemetry/   # Data decoding & Anomaly analysis
│   └── dashboard/   # Real-time UI implementation
└── tests/           # Unit tests for physics and encoding logic