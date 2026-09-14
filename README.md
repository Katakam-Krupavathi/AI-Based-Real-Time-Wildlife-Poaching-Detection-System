# 🌿 SANJEEVANI
### AI-Based Real-Time Wildlife Poaching Detection System

![Python](https://img.shields.io/badge/Python-3.9-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-DeepLearning-red)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-green)
![Computer Vision](https://img.shields.io/badge/ComputerVision-WildlifeAI-orange)
![Status](https://img.shields.io/badge/Status-ResearchPrototype-success)

---

## 🧠 Project Overview

**SANJEEVANI** is an AI-powered wildlife protection system designed to detect potential poaching activity using **computer vision and acoustic gunshot detection**.

The system automatically identifies suspicious activity and alerts forest rangers in real time.

### Domains

Artificial Intelligence  
Computer Vision  
Edge AI  
Wildlife Monitoring  
IoT Surveillance

---

# 🌍 Problem Statement

Wildlife poaching is a major threat to endangered species worldwide.

Forest departments struggle to monitor vast forest areas because of:

- 👮 Limited ranger manpower
- 🌳 Dense forest visibility issues
- ⏱️ Delayed threat reporting
- 📡 Lack of automated monitoring systems

Poachers frequently operate with **firearms and camouflage**, making detection extremely difficult using conventional surveillance systems.

### 🎯 Objective

Develop an AI system capable of automatically detecting poaching threats using:

- 🧠 Computer Vision
- 🔊 Gunshot Audio Detection
- 🤖 AI-based Threat Classification
- 📱 Automated Ranger Alert System

```text
Camera / Drone Feed
│
▼
YOLOv8 Object Detection
(human, gun, elephant, jacket)
│
▼
Threat Logic Engine
│
▼
Poacher Classification
│
┌───────────────┬───────────────┬───────────────┐
▼ ▼ ▼
SMS Alert LoRa Message Evidence Logging
│
▼
Map Visualization
```

---

# 🤖 Object Detection Model

**Model:** YOLOv8s  
**Framework:** PyTorch  
**Library:** Ultralytics

### Detected Classes

| Class ID | Object |
|--------|--------|
| 0 | 🔫 Gun |
| 1 | 🐘 Elephant |
| 2 | 👤 Human |
| 3 | 🦺 Ranger Jacket |

### Threat Interpretation

| Detection | Interpretation |
|-----------|---------------|
| human + jacket | Ranger |
| human without jacket | Poacher |
| human + gun | Armed Poacher |

---

# ⚙️ YOLO Training Configuration

```python
model = "yolov8s.pt"

imgsz = 832
epochs = 60
batch = 16

optimizer = "AdamW"
lr0 = 0.0008

freeze = 10
patience = 20

# augmentations
mosaic = 1.0
mixup = 0.2
scale = 0.9
translate = 0.2
degrees = 10
shear = 2
fliplr = 0.5

# color augmentation
hsv_h = 0.015
hsv_s = 0.7
hsv_v = 0.4
```
## 💻 Hardware Used

| Component | Value |
|----------|------|
| GPU | NVIDIA RTX 4060 Laptop GPU |
| CUDA | 12.1 |
| Framework | PyTorch 2.5.1 |

---

## 📂 Dataset

| Dataset | Size |
|--------|------|
| Images | 200+ |
| Audio | 2000+ |

### Data Sources

- **Gunshot Audio Dataset**  
  https://www.kaggle.com/datasets/emrahaydemr/gunshot-audio-dataset  

- **Noise Audio Dataset**  
  https://www.kaggle.com/datasets/javohirtoshqorgonov/noise-audio-data  

- **Elephant Thermal Images**  
  https://www.kaggle.com/datasets/shijo96john/elephant-thermal-images  

- **Elephant Image Dataset**  
  https://www.kaggle.com/datasets/vivmankar/asian-vs-african-elephant-image-classification  

- Additional **synthetic images generated using DALL·E**

---

# 📈 YOLO Model Performance

## Overall Metrics

| Metric | Value |
|------|------|
| Precision | 0.856 |
| Recall | 0.855 |
| mAP@0.5 | 0.914 |
| mAP@0.5:0.95 | 0.566 |

---

## Per-Class Results

| Class | Precision | Recall | mAP50 | mAP50-95 |
|------|------|------|------|------|
| Gun | 1.00 | 0.651 | 0.796 | 0.354 |
| Elephant | 0.851 | 0.880 | 0.881 | 0.578 |
| Human | 0.941 | 0.889 | 0.984 | 0.536 |
| Jacket | 0.631 | 1.00 | 0.995 | 0.796 |

**Best model stored at**
`best.pt` (repository root)


---

# ⚡ Inference Speed

| Stage | Time |
|------|------|
| Preprocessing | 0.8 ms |
| Inference | 7.0 ms |
| Postprocessing | 1.7 ms |

**Total ≈ 9.5 ms per image**

---

# 🔊 Gunshot Detection Model

Binary **audio classifier** trained to identify firearm sounds.

## Audio Features

- Log Mel Spectrogram
- MFCC
- Spectral Centroid
- Spectral Rolloff
- RMS Energy
- Zero Crossing Rate
- Delta Features

These are **stacked into multi-channel audio feature tensors**.

---

# 📊 Gunshot Model Performance

**Validation Samples:** 807

## Confusion Matrix

| | Pred 0 | Pred 1 |
|---|---|---|
| Actual 0 | 348 | 57 |
| Actual 1 | 2 | 400 |

---

## Classification Metrics

| Class | Precision | Recall | F1 |
|------|------|------|------|
| Non-Gunshot | 0.99 | 0.86 | 0.92 |
| Gunshot | 0.88 | 1.00 | 0.93 |

**Overall Accuracy: 93%**

---

# 🚨 Threat Classification Logic

| Rule | Result |
|-----|------|
| human + jacket | Ranger |
| human only | Poacher |
| human + gun | Armed Poacher |
| Gunshot detected | Critical Alert |

---

# 🧩 System Components

| File | Purpose |
|------|------|
| `central_server.py` | Main system controller |
| `threat_logic.py` | Threat classification logic |
| `yolo_detector.py` | YOLO object detection |
| `gunshot_detector.py` | Gunshot detection |
| `proximity_utils.py` | Distance calculations |
| `config.py` | System configuration |
| `lora_handshake.py` | Ranger communication |
| `ranger_device_sim.py` | Ranger device simulator |
| `sms_alert.py` | SMS alert module |
| `evidence_logger.py` | Evidence logging |
| `map_generator.py` | Event map generation |
| `data.yaml` | YOLO dataset configuration |

---

# 🚨 System Output

When a **poacher event is detected**:

1️⃣ Evidence is logged  
2️⃣ SMS alerts sent to rangers  
3️⃣ LoRa alert transmitted  
4️⃣ Event location updated on monitoring map  

---

## 🛠️ Quick Start & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy `.env.example` to `.env` and set your optional credentials:
```bash
cp .env.example .env
```

### 3. Run Central Server
```bash
python automation_scripts/central_server.py
```

---

# 🚀 Future Improvements

🔥 Thermal camera integration  

🚁 Drone surveillance automation  

🎯 Multi-frame object tracking  

🛰 Satellite monitoring  

🤖 Ranger patrol prediction using AI
