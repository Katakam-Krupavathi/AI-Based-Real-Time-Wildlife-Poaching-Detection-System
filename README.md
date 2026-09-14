# 🌿 SANJEEVANI: AI-Based Real-Time Wildlife Poaching Detection System

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.5.1-EE4C2C.svg)](https://pytorch.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FF00.svg)](https://github.com/ultralytics/ultralytics)
[![Flask](https://img.shields.io/badge/Flask-3.1-black.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF.svg)](https://github.com/features/actions)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)

> **SANJEEVANI** is an autonomous, multi-modal IoT surveillance and early warning platform designed to protect endangered wildlife from illegal poaching incursions. It combines computer vision (YOLOv8), bioacoustic gunshot analysis (deep audio CNN), cryptographic LoRa ranger deconfliction, multi-frame spatial tracking, and interactive tactical GIS mapping.

---

## 📸 System Architecture & Pipeline

```
                              ┌─────────────────────────────────────────────────┐
                              │           EDGE SENSOR / DRONE / TRAP            │
                              │  [ Optical / IR Camera ]   [ Acoustic Sensors ] │
                              │  [ LoRa RSSI Beacon ]      [ GPS Telemetry ]    │
                              └────────────────────────┬────────────────────────┘
                                                       │
                                  HTTP POST /process_multimodal
                                                       │
                                                       ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   SANJEEVANI CENTRAL COMMAND SERVER                                   │
│                                                                                                        │
│  ┌─────────────────────────┐   ┌──────────────────────────┐   ┌─────────────────────────────────────┐  │
│  │   YOLOv8 Vision Model   │   │  Acoustic Gunshot Model  │   │     LoRa Cryptographic Beacon       │  │
│  │  (Gun, Elephant, Human, │   │ (Log-Mel + Delta CNN)    │   │  (HMAC Deconfliction & RSSI Tag)    │  │
│  │         Jacket)         │   │                          │   │                                     │  │
│  └────────────┬────────────┘   └────────────┬─────────────┘   └──────────────────┬──────────────────┘  │
│               │                             │                                    │                     │
│               ▼                             ▼                                    ▼                     │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                 MULTI-MODAL THREAT ARBITRATION & SPATIAL FUSION ENGINE                           │  │
│  │  - Euclidean Bounding-Box Proximity Analysis (BBOX_PROXIMITY_PX)                                 │  │
│  │  - Confidence-Weighted Incident Scoring (0.0 to 1.0)                                             │  │
│  │  - Multi-Frame Centroid Tracking & Debouncing (CentroidTracker)                                  │  │
│  │  - Acoustic-Visual Combat Escalation (Tier 1 -> Tier 4)                                          │  │
│  └──────────────────────────────────────────┬───────────────────────────────────────────────────────┘  │
│                                             │                                                          │
│                 ┌───────────────────────────┼───────────────────────────┐                              │
│                 ▼                           ▼                           ▼                              │
│  ┌─────────────────────────────┐ ┌────────────────────┐ ┌───────────────────────────────┐              │
│  │    Tactical Folium Map      │ │ SMS / Twilio Alert │ │  Live Web Command Center UI   │              │
│  │  (Dynamic Threat Heatmap)   │ │  (Ranger Dispatch) │ │  (Dark Theme HUD & Telemetry) │              │
│  └─────────────────────────────┘ └────────────────────┘ └───────────────────────────────┘              │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Features

- 👁️ **High-Speed Object Detection**: Custom YOLOv8s model trained to identify firearms (`gun`), endangered wildlife (`elephant`), intruders (`human`), and authorized ranger gear (`jacket`).
- 🔊 **Acoustic Gunshot Classifier**: Deep convolutional network consuming stacked Log-Mel spectrograms + delta features with 93% real-world gunshot classification accuracy.
- 🛡️ **LoRa Ranger Deconfliction**: Authorized field personnel transmitting authenticated LoRa beacons (RSSI $\ge -70\text{ dBm}$) are verified to prevent false alarms.
- 🎯 **Multi-Frame Tracking & Debounce**: Built-in `CentroidTracker` assigns persistent track IDs across camera frames and debounces repeated SMS alerts.
- 🗺️ **Tactical GIS Map Engine**: Generates interactive Folium satellite layers with color-coded threat zones (Red = Gunshot/Armed, Orange = Intrusion, Green = Ranger).
- 📊 **Real-Time HUD Command Center**: Glassmorphic dark-mode web dashboard featuring live telemetry, incident counters, evidence snapshots, and automated map updates.
- 🩺 **Automated Health Diagnostic**: `/health` self-test verifying YOLO weights, TensorFlow models, normalization files, Twilio keys, and storage directories.

---

## 🚨 Threat Arbitration Hierarchy

| Tier | Threat Level | Trigger Condition | Automated Response |
|:---:|:---|:---|:---|
| **Tier 1** | 🔴 `CRITICAL_ARMED_COMBAT` | Armed poacher + visual weapon proximity OR acoustic gunshot + visual intruder | Instant SMS dispatch, visual evidence capture, map alert broadcast |
| **Tier 2** | 🔊 `ACOUSTIC_GUNSHOT_ALERT` | Bioacoustic gunshot model probability $\ge 0.50$ | Audio logged, SMS dispatched with GPS coordinates |
| **Tier 3** | ⚠️ `SUSPECTED_POACHER_INTRUSION` | Human detected without ranger jacket or valid LoRa beacon | Visual evidence saved, ranger dispatch advised |
| **Tier 4** | 🛡️ `RANGER_PATROL_MONITORED` | Human detected with verified LoRa beacon (RSSI $\ge -70\text{ dBm}$) | Sector logged as monitored, no alarm triggered |
| **Tier 4** | 🌿 `NO_THREAT` | Wildlife (Elephant) detected in sector | Wildlife logged safe, baseline surveillance maintained |

---

## 📊 Model Evaluation & Benchmarks

### YOLOv8s Object Detector

| Class | Precision | Recall | mAP@0.5 | mAP@0.5:0.95 |
|:---|:---:|:---:|:---:|:---:|
| 🔫 **Gun** | **1.000** | 0.651 | 0.796 | 0.354 |
| 🐘 **Elephant** | 0.851 | 0.880 | 0.881 | 0.578 |
| 👤 **Human** | **0.941** | 0.889 | **0.984** | 0.536 |
| 🦺 **Ranger Jacket** | 0.631 | **1.000** | **0.995** | **0.796** |
| **All Classes** | **0.856** | **0.855** | **0.914** | **0.566** |

- **Inference Latency**: $\approx 9.5\text{ ms}$ per frame on NVIDIA RTX 4060 GPU / $\approx 45\text{ ms}$ on modern CPU.

### Acoustic Gunshot Classifier

- **Validation Samples**: 807
- **Overall Accuracy**: **93.0%**
- **Gunshot Recall**: **100.0%** (0 false negatives for firearm discharges)
- **Non-Gunshot Precision**: **99.0%**

---

## 🌐 API Reference

| Endpoint | Method | Description |
|:---|:---:|:---|
| `/` | `GET` | Renders the live tactical command center dashboard UI. |
| `/health` | `GET` | Performs self-test diagnostics across models, Twilio, and storage. |
| `/process` | `POST` | Processes visual camera traps (`image`, `lat`, `lon`, `device_id`, `rssi`). |
| `/process_multimodal` | `POST` | Processes synchronized visual + acoustic feeds (`image`, `audio`, `lat`, `lon`, `rssi`). |
| `/api/events` | `GET` | Fetches recent incident logs, telemetry, and aggregate detection statistics. |
| `/api/latest-map` | `GET` | Serves the dynamically updated Folium tactical surveillance map. |
| `/evidence/<filename>` | `GET` | Serves high-resolution annotated threat evidence images. |

---

## 🚀 Quick Start & Installation

### Option 1: Native Python

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Katakam-Krupavathi/AI-Based-Real-Time-Wildlife-Poaching-Detection-System.git
   cd AI-Based-Real-Time-Wildlife-Poaching-Detection-System
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables (Optional)**:
   ```bash
   cp .env.example .env
   ```

4. **Run End-to-End Demonstration Suite**:
   ```bash
   python demo.py
   ```

5. **Start Live Command Center**:
   ```bash
   python automation_scripts/central_server.py
   ```
   Open `http://localhost:5000` in your web browser.

---

### Option 2: Docker & Docker Compose

Deploy the complete SANJEEVANI surveillance stack in a container:

```bash
docker-compose up --build
```

Access the command center at `http://localhost:5000`.

---

## 📁 Repository Structure

```
├── automation_scripts/
│   ├── central_server.py       # Flask multi-modal command server & API routes
│   ├── threat_logic.py         # Multi-modal arbitration & confidence scoring engine
│   ├── yolo_detector.py        # Ultralytics YOLOv8 detector interface
│   ├── gunshot_detector.py     # Bioacoustic spectrogram CNN classifier
│   ├── tracker.py              # Multi-frame centroid tracker & alert debouncer
│   ├── map_generator.py        # Tactical Folium GIS mapping utility
│   ├── sms_alert.py            # Twilio SMS dispatcher with mock fallback
│   ├── evidence_logger.py      # Annotated visual evidence persistence
│   ├── proximity_utils.py      # Spatial Euclidean bounding-box geometry
│   ├── lora_handshake.py       # LoRa cryptographic authentication
│   ├── ranger_device_sim.py    # Ranger IoT beacon simulator
│   └── config.py               # Centralized configuration & environment loader
├── templates/
│   └── dashboard.html          # Glassmorphic HUD Command Center web UI
├── Dataset Samples/            # Sample visual & acoustic test assets
├── .github/workflows/
│   └── ci.yml                  # GitHub Actions CI automated verification
├── demo.py                     # Synthetic end-to-end verification script
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Container orchestration
├── requirements.txt            # Python dependencies
├── best.pt                     # Trained YOLOv8s weights
├── gunshot_model_v3.h5         # Trained gunshot CNN model
├── train_mean.npy              # Audio normalization mean tensor
├── train_std.npy               # Audio normalization standard deviation tensor
└── README.md                   # System documentation
```

---

## 🛡️ License & Acknowledgements

Developed for wildlife conservation and anti-poaching operations. Distributed under the MIT License.
