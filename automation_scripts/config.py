# config.py

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

YOLO_MODEL_PATH = os.path.join(PROJECT_ROOT, "best.pt")
GUNSHOT_MODEL_PATH = os.path.join(PROJECT_ROOT, "gunshot_model_v3.h5")
MEAN_PATH = os.path.join(PROJECT_ROOT, "train_mean.npy")
STD_PATH = os.path.join(PROJECT_ROOT, "train_std.npy")

DAILY_PASSCODE = "9382"  # Change daily

LORA_SECRET_KEY = "RANGER_SECRET_2025"

PROXIMITY_RSSI_THRESHOLD = -70  # adjust based on testing

SERVER_PORT = 5000