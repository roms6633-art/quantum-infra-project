# 🛡️ Quantum-Safe Infrastructure: QKD Simulation Dashboard

An advanced, modular Quantum Key Distribution (QKD) simulation platform. This project demonstrates a real-world **Quantum Network Operation Center (NOC)**, integrating Quantum Physics, Cryptography, and Modern Software Architecture.

---

## 🚀 Key Features

* **📡 Live Protocol Monitor:** Real-time execution of **BB84** and **E91** protocols using **IBM Qiskit**. Includes simulated eavesdropping detection.
* **📉 Fiber Attenuation & QBER:** Models photon loss (0.2 dB/km) and monitors the **Quantum Bit Error Rate** in real-time.
* **🔐 Privacy Amplification:** Implements **SHA-256** hashing to eliminate information leakage and secure the final key.
* **📊 Entropy Analytics:** Calculates **Shannon Entropy** to verify the unpredictability of the quantum randomness.
* **📟 Security Event Log:** A live, terminal-style log for NOC monitoring with unique cryptographic signatures (ENC_SIG).

---

## 🏗️ System Architecture

The project is built with a **Modular Blueprint Architecture**, making it scalable and enterprise-ready:

```text
quantum-infra/
├── app.py              # Flask Server & Blueprint Registration
├── routes/             # Backend Logic Modules
│   ├── monitor.py      # Qiskit Circuit Logic
│   ├── attenuation.py  # Physical Layer Simulation
│   ├── privacy.py      # Cryptographic Post-processing
│   └── analytics.py    # Statistical Engine
├── templates/          # Dynamic Dashboard (HTML5/JS)
└── Dockerfile          # Containerization Environment