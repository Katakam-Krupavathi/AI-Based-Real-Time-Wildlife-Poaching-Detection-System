# yolo_detector.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ultralytics import YOLO
import config

_model = None

def get_yolo_model():
    global _model
    if _model is None:
        _model = YOLO(config.YOLO_MODEL_PATH)
    return _model

def detect_objects(frame, conf=0.43, iou=0.5):
    model = get_yolo_model()
    results = model.predict(frame, conf=conf, iou=iou, verbose=False)
    detections = []

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0].item()) if hasattr(box.cls[0], "item") else int(box.cls[0])
            class_name = model.names[cls_id]
            conf_score = float(box.conf[0].item()) if hasattr(box.conf[0], "item") else float(box.conf[0])

            coords = box.xyxy[0].tolist() if hasattr(box.xyxy[0], "tolist") else list(box.xyxy[0])
            x1, y1, x2, y2 = coords
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0

            detections.append({
                "label": class_name,
                "center": (cx, cy),
                "conf": conf_score,
                "box": [float(x1), float(y1), float(x2), float(y2)]
            })

    return detections, results