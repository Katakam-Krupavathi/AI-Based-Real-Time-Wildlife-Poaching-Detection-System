# config.py
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    # Base directory of the repository
    BASE_DIR = Path(__file__).resolve().parent.parent
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()
except ImportError:
    BASE_DIR = Path(__file__).resolve().parent.parent

PROJECT_ROOT = os.getenv("PROJECT_ROOT", str(BASE_DIR))

# Model and artifact paths
YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", os.path.join(PROJECT_ROOT, "best.pt"))
GUNSHOT_MODEL_PATH = os.getenv("GUNSHOT_MODEL_PATH", os.path.join(PROJECT_ROOT, "gunshot_model_v3.h5"))
MEAN_PATH = os.getenv("MEAN_PATH", os.path.join(PROJECT_ROOT, "train_mean.npy"))
STD_PATH = os.getenv("STD_PATH", os.path.join(PROJECT_ROOT, "train_std.npy"))

# Proximity Thresholds
BBOX_PROXIMITY_PX = int(os.getenv("BBOX_PROXIMITY_PX", 150))
LORA_RSSI_THRESHOLD = float(os.getenv("LORA_RSSI_THRESHOLD", -70))

# Security & LoRa Handshake
DAILY_PASSCODE = os.getenv("DAILY_PASSCODE", "9382")
LORA_SECRET_KEY = os.getenv("LORA_SECRET_KEY", "RANGER_SECRET_2025")

# Twilio Alerts Configuration
TWILIO_SID = os.getenv("TWILIO_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN", "")
TWILIO_FROM = os.getenv("TWILIO_FROM", "")
TWILIO_TO = os.getenv("TWILIO_TO", "")

# Server
SERVER_PORT = int(os.getenv("PORT", 5000))