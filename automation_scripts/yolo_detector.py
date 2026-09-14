# yolo_detector.py

from ultralytics import YOLO
import config

model = YOLO(config.YOLO_MODEL_PATH)

def detect_objects(frame):
    results = model.predict(frame, conf=0.43, iou=0.5)
    detected_classes = []

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id]
            detected_classes.append(class_name)

    return detected_classes, results