from flask import Flask, request
import cv2
import numpy as np
from yolo_detector import detect_objects
from threat_logic import decide_threat
from sms_alert import send_sms
from map_generator import generate_map
from evidence_logger import save_evidence
import config

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_data():

    file = request.files['image']
    lat = request.form.get("latitude")
    lon = request.form.get("longitude")

    image_bytes = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

    detected_classes, results = detect_objects(frame)

    # Simulated RSSI from LoRa
    rssi_value = -60  # simulate close proximity

    decision = decide_threat(detected_classes, rssi_value)

    if decision != "No Threat":

        save_evidence(file)
        generate_map(lat, lon)

        message = f"""
🚨 ALERT: {decision}
Location: {lat}, {lon}
"""

        send_sms(message)

    return {"decision": decision}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.SERVER_PORT)