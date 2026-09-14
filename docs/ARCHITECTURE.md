# 🏛️ SANJEEVANI System Architecture & Technical Design

## 1. High-Level System Architecture

```mermaid
flowchart TD
    subgraph EdgeSensors["📡 Edge Surveillance & Sensor Nodes"]
        A1["📷 Optical / Thermal Camera Trap"]
        A2["🎙️ Bioacoustic Directional Microphone"]
        A3["📡 LoRa Ranger Transceiver (RSSI + HMAC)"]
        A4["🛰️ GPS Telemetry Unit"]
    end

    subgraph CentralServer["🖥️ SANJEEVANI Central Command Server"]
        B1["🌐 REST Ingestion Engine (/process, /process_multimodal)"]
        
        subgraph AIInference["🧠 Multi-Modal AI Inference Pipeline"]
            C1["👁️ YOLOv8s Vision Model<br/>(Gun, Elephant, Human, Jacket)"]
            C2["🔊 Deep Audio CNN Classifier<br/>(Log-Mel + Delta Spectrograms)"]
            C3["🔐 LoRa Cryptographic Deconfliction<br/>(HMAC + Daily Passcode + RSSI)"]
        end
        
        subgraph ThreatEngine["⚖️ Threat Arbitration & Tracking"]
            D1["📐 Spatial Geometry Engine<br/>(Bounding Box Distance & Center Px)"]
            D2["🎯 CentroidTracker<br/>(Multi-Frame ID & Cooldown Debounce)"]
            D3["📊 Confidence-Weighted Fusion<br/>(Composite Risk Scoring 0.0 - 1.0)"]
        end
        
        subgraph AlertDispatch["🚨 Dispatch & Visualization"]
            E1["📱 SMS Alert Gateway (Twilio / Mock Fallback)"]
            E2["🗺️ Tactical GIS Map Generator (Folium Satellite Heatmap)"]
            E3["💾 Forensic Evidence Logger (Annotated Frames & Timestamps)"]
            E4["📊 Live Web HUD Command Center (Real-Time Telemetry)"]
        end
    end

    EdgeSensors -->|HTTP Multipart / LoRa Gateway| B1
    B1 --> C1 & C2 & C3
    C1 & C2 & C3 --> D1 & D2 & D3
    D1 & D2 & D3 --> E1 & E2 & E3 & E4
```

---

## 2. Multi-Modal Processing & Threat Arbitration Sequence

```mermaid
sequenceDiagram
    autonumber
    participant Node as 📡 Edge Sensor Node
    participant Server as 🖥️ Central Server
    participant Vision as 👁️ YOLOv8 Detector
    participant Audio as 🔊 Gunshot CNN
    participant Tracker as 🎯 Centroid Tracker
    participant Logic as ⚖️ Threat Arbitration
    participant Dispatch as 🚨 SMS & Map Dispatch

    Node->>Server: POST /process_multimodal (Image + Audio + RSSI + GPS)
    par Visual Inference
        Server->>Vision: Forward Image Frame
        Vision-->>Server: Detections (boxes, classes, confidences)
    and Acoustic Inference
        Server->>Audio: Forward Audio Waveform
        Audio-->>Server: Gunshot Probability (0.0 - 1.0)
    end

    Server->>Tracker: Update Object Centroids & Track IDs
    Tracker-->>Server: Tracked Objects + is_new_alert Flags

    Server->>Logic: Run Threat Arbitration (Vision + Audio + LoRa RSSI)
    Note over Logic: Calculate Spatial Proximity<br/>Check Ranger RSSI >= -70 dBm<br/>Fuse Multi-Modal Threat Tier

    alt Threat Tier 1 or Tier 2 (Critical / Gunshot)
        Logic->>Dispatch: Trigger Emergency SMS to Rangers
        Logic->>Dispatch: Save Annotated Evidence Image
        Logic->>Dispatch: Re-render Folium Incident Map
    else Threat Tier 4 (Ranger or Wildlife)
        Logic->>Dispatch: Log Safe Telemetry to Dashboard
    end

    Server-->>Node: 200 OK (Decision, Fused Score, Urgency, Event Summary)
```

---

## 3. Threat Arbitration Hierarchy

```mermaid
stateDiagram-v2
    [*] --> Ingestion

    state Ingestion {
        [*] --> CheckAudio
        [*] --> CheckVision
    }

    Ingestion --> GunshotDetected: Audio Prob >= 0.50
    Ingestion --> VisualAnalysis: Audio Prob < 0.50

    state VisualAnalysis {
        [*] --> CheckClasses
        CheckClasses --> RangerVerified: Human + Jacket OR RSSI >= -70dBm
        CheckClasses --> ArmedPoacher: Human + Gun Proximity (< 250px)
        CheckClasses --> Intruder: Human Only (No Beacon)
        CheckClasses --> WildlifeSafe: Elephant Only
    }

    GunshotDetected --> Tier1_ArmedCombat: Intruder Also Visible
    GunshotDetected --> Tier2_GunshotAlert: No Visual Target

    ArmedPoacher --> Tier1_ArmedCombat
    Intruder --> Tier3_PoacherIntrusion
    RangerVerified --> Tier4_RangerMonitored
    WildlifeSafe --> Tier4_NoThreat

    Tier1_ArmedCombat --> CriticalResponse: SMS + Map + Forensic Evidence
    Tier2_GunshotAlert --> HighResponse: SMS + Audio Evidence
    Tier3_PoacherIntrusion --> MediumResponse: Forensic Evidence + Advisory
    Tier4_RangerMonitored --> NormalLogging: Dashboard Log
    Tier4_NoThreat --> NormalLogging: Baseline Safe
```

---

## 4. Multi-Frame Tracking & Debounce Mechanism

To eliminate duplicate SMS alerts when poachers remain in camera trap view for multiple seconds:

1. **Centroid Registration**: Detected bounding box centers $(C_x, C_y)$ are calculated.
2. **Euclidean Matching**: Minimum Euclidean distance matching links detections across successive frames.
3. **Alert Cooldown Window**: Each registered track ID maintains a `last_alert_time` timestamp. An alert is only dispatched if $\Delta t > \text{ALERT\_COOLDOWN\_SEC}$ (default: 30 seconds).
4. **Deregistration**: Objects absent for more than `MAX_DISAPPEARED` frames (default: 10 frames) are purged from memory.
