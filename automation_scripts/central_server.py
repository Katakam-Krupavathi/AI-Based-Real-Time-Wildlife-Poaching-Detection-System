from flask import Flask, request, jsonify
import cv2
import numpy as np
import config
from yolo_detector import detect_objects
from threat_logic import analyze_detections
from sms_alert import send_sms
from map_generator import generate_map
from evidence_logger import save_evidence

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_data():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided in request"}), 400

    file = request.files['image']
    lat = request.form.get("latitude", "12.9716")
    lon = request.form.get("longitude", "77.5946")

    # Read image bytes into OpenCV frame
    image_bytes = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"error": "Failed to decode image"}), 400

    # Reset file pointer for evidence saving
    file.seek(0)

    # Detect objects and extract centers & bounding boxes
    detections, results = detect_objects(frame)

    # Analyze threat events via bounding box proximity logic
    threat_events = analyze_detections(detections)

    # Determine primary threat status
    if not threat_events:
        detected_labels = [d["label"] for d in detections]
        if "elephant" in detected_labels:
            decision = "WILDLIFE_MONITORED"
        else:
            decision = "NO_THREAT"
    else:
        event_types = [e["type"] for e in threat_events]
        if "ARMED_POACHER" in event_types:
            decision = "CRITICAL_ARMED_POACHER"
        elif "POACHER_EVENT" in event_types:
            decision = "SUSPECTED_POACHER"
        elif "RANGER" in event_types:
            decision = "RANGER_PATROL_VERIFIED"
        else:
            decision = threat_events[0]["type"]

    # If poacher activity is detected, trigger evidence logging, alert map, and SMS
    if decision in ["CRITICAL_ARMED_POACHER", "SUSPECTED_POACHER"]:
        save_evidence(file)
        generate_map(lat, lon)

        message = (
            f"🚨 SANJEEVANI ALERT: {decision}\n"
            f"Location: {lat}, {lon}\n"
            f"Threat signatures: {len(threat_events)}"
        )
        send_sms(message)

    return jsonify({
        "decision": decision,
        "threat_events": threat_events,
        "detections_count": len(detections),
        "latitude": lat,
        "longitude": lon
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.SERVER_PORT)