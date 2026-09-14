import sys
import os
from datetime import datetime
from pathlib import Path

# Add automation_scripts to system path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from flask import Flask, request, jsonify, render_template, send_from_directory, send_file
import cv2
import numpy as np
import config
from yolo_detector import detect_objects, get_yolo_model
from threat_logic import analyze_detections, fuse_multimodal_threat
from gunshot_detector import detect_gunshot, get_model as get_gunshot_model, get_norm_stats
from tracker import CentroidTracker
from sms_alert import send_sms
from map_generator import generate_map
from evidence_logger import save_evidence

# Initialize Flask app pointing to root templates folder
template_dir = os.path.join(config.PROJECT_ROOT, "templates")
app = Flask(__name__, template_folder=template_dir)

# Initialize tracking & state
tracker = CentroidTracker(max_disappeared=30, max_distance_px=config.BBOX_PROXIMITY_PX)
EVENT_HISTORY = []
STATS = {
    "armed_poachers": 0,
    "gunshots": 0,
    "rangers": 0,
    "wildlife": 0,
    "total": 0
}


@app.route('/')
def dashboard_view():
    """Renders the live command center dashboard."""
    return render_template("dashboard.html")


@app.route('/health', methods=['GET'])
def health_check():
    """
    Diagnostic self-test endpoint.
    Verifies YOLO weights, gunshot acoustic model, normalization files,
    Twilio alert configuration, and storage write permissions.
    """
    diagnostics = {}
    status = "HEALTHY"

    # 1. YOLO Model Check
    try:
        yolo = get_yolo_model()
        diagnostics["yolo_model"] = {
            "status": "LOADED",
            "weights_path": config.YOLO_MODEL_PATH,
            "classes": list(yolo.names.values())
        }
    except Exception as e:
        status = "DEGRADED"
        diagnostics["yolo_model"] = {"status": "ERROR", "error": str(e)}

    # 2. Gunshot Model Check
    try:
        gunshot = get_gunshot_model()
        mean_v, std_v = get_norm_stats()
        diagnostics["gunshot_model"] = {
            "status": "LOADED",
            "model_path": config.GUNSHOT_MODEL_PATH,
            "train_mean": float(mean_v),
            "train_std": float(std_v)
        }
    except Exception as e:
        status = "DEGRADED"
        diagnostics["gunshot_model"] = {"status": "ERROR", "error": str(e)}

    # 3. Twilio SMS Alerts Check
    has_twilio = bool(
        config.TWILIO_SID and config.TWILIO_TOKEN
        and not config.TWILIO_SID.startswith("your_")
    )
    diagnostics["sms_dispatch"] = {
        "mode": "LIVE_TWILIO" if has_twilio else "SIMULATION_LOG",
        "sender": config.TWILIO_FROM if has_twilio else "N/A (Mock)",
        "recipient": config.TWILIO_TO if has_twilio else "N/A (Mock)"
    }

    # 4. Storage & Evidence Check
    evidence_dir = os.path.join(config.PROJECT_ROOT, "evidence")
    try:
        os.makedirs(evidence_dir, exist_ok=True)
        test_file = os.path.join(evidence_dir, ".health_check_tmp")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        diagnostics["storage"] = {"status": "WRITABLE", "path": evidence_dir}
    except Exception as e:
        status = "DEGRADED"
        diagnostics["storage"] = {"status": "ERROR", "error": str(e)}

    # 5. LoRa Security Check
    diagnostics["lora_security"] = {
        "rssi_threshold_dbm": config.LORA_RSSI_THRESHOLD,
        "daily_passcode_configured": bool(config.DAILY_PASSCODE),
        "secret_key_configured": bool(config.LORA_SECRET_KEY)
    }

    return jsonify({
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "diagnostics": diagnostics
    }), 200 if status == "HEALTHY" else 207


@app.route('/api/events', methods=['GET'])
def get_events_api():
    """Returns recent threat events and aggregate stats for live dashboard UI."""
    evidence_dir = os.path.join(config.PROJECT_ROOT, "evidence")
    recent_images = []
    if os.path.exists(evidence_dir):
        files = sorted(
            [f for f in os.listdir(evidence_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))],
            key=lambda x: os.path.getmtime(os.path.join(evidence_dir, x)),
            reverse=True
        )
        recent_images = files[:12]

    return jsonify({
        "events": list(reversed(EVENT_HISTORY[-50:])),
        "stats": STATS,
        "recent_evidence": recent_images
    })


@app.route('/api/latest-map', methods=['GET'])
def get_latest_map():
    """Serves the latest tactical Folium map HTML."""
    map_path = os.path.join(config.PROJECT_ROOT, "latest_alert_map.html")
    if not os.path.exists(map_path):
        # Generate default map if none exists
        generate_map(11.6854, 76.1320)
    return send_file(map_path)


@app.route('/evidence/<path:filename>', methods=['GET'])
def get_evidence_file(filename):
    """Serves captured evidence photos for inspection."""
    evidence_dir = os.path.join(config.PROJECT_ROOT, "evidence")
    return send_from_directory(evidence_dir, filename)


@app.route('/process', methods=['POST'])
def process_data():
    """
    Standard visual stream ingestion route.
    Performs YOLO inference, object tracking, threat analysis, evidence logging,
    map plotting, and SMS dispatch.
    """
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided in request"}), 400

    file = request.files['image']
    lat = request.form.get("latitude", "11.6854")
    lon = request.form.get("longitude", "76.1320")

    image_bytes = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"error": "Failed to decode image"}), 400

    file.seek(0)

    # 1. Run YOLO detection
    detections, results = detect_objects(frame)

    # 2. Update multi-frame tracker
    tracked_detections = tracker.update(detections)

    # 3. Analyze threat logic with confidence weighting
    threat_events = analyze_detections(tracked_detections)

    # 4. Multi-modal fusion evaluation
    multimodal = fuse_multimodal_threat(threat_events, gunshot_detected=False, gunshot_prob=0.0)
    decision = multimodal["decision"]

    # Check wildlife counts
    elephant_count = sum(1 for d in detections if d.get("label") == "elephant")
    if elephant_count > 0:
        STATS["wildlife"] += elephant_count

    # Update stats based on threat
    if "ARMED" in decision:
        STATS["armed_poachers"] += 1
    elif "RANGER" in decision:
        STATS["rangers"] += 1
    STATS["total"] += 1

    evidence_file = None
    # 5. Check if actionable new alert requires dispatch
    has_new_alert = any(e.get("is_new_alert", True) for e in threat_events)
    if multimodal["requires_immediate_dispatch"] and has_new_alert:
        saved_path = save_evidence(file)
        evidence_file = os.path.basename(saved_path) if saved_path else None
        generate_map(lat, lon)

        max_conf = max([e.get("confidence_pct", "N/A") for e in threat_events], default="N/A")
        message = (
            f"🚨 WILDLIFE POACHING ALERT: {decision}\n"
            f"Confidence: {max_conf}\n"
            f"Location: {lat}, {lon}\n"
            f"Signatures: {multimodal['summary']}"
        )
        send_sms(message)

    # 6. Append to in-memory event stream
    event_entry = {
        "id": len(EVENT_HISTORY) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "decision": decision,
        "urgency": multimodal["urgency"],
        "fused_score": multimodal["fused_score"],
        "summary": multimodal["summary"],
        "latitude": lat,
        "longitude": lon,
        "detections_count": len(detections),
        "threat_events": threat_events,
        "evidence_file": evidence_file,
        "audio_gunshot": False
    }
    EVENT_HISTORY.append(event_entry)

    return jsonify({
        "decision": decision,
        "urgency": multimodal["urgency"],
        "fused_score": multimodal["fused_score"],
        "summary": multimodal["summary"],
        "threat_events": threat_events,
        "detections_count": len(detections),
        "latitude": lat,
        "longitude": lon,
        "evidence_saved": bool(evidence_file)
    })


@app.route('/process_multimodal', methods=['POST'])
def process_multimodal():
    """
    Unified multi-modal route: ingests synchronized visual frames and acoustic audio.
    Fuses confidence scores across both modalities into a unified priority tier.
    """
    lat = request.form.get("latitude", "11.6854")
    lon = request.form.get("longitude", "76.1320")

    threat_events = []
    detections = []
    evidence_file = None

    # Process image if provided
    if 'image' in request.files:
        img_file = request.files['image']
        image_bytes = np.frombuffer(img_file.read(), np.uint8)
        frame = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
        if frame is not None:
            img_file.seek(0)
            detections, _ = detect_objects(frame)
            tracked = tracker.update(detections)
            threat_events = analyze_detections(tracked)

    # Process audio if provided
    gunshot_detected = False
    gunshot_prob = 0.0
    if 'audio' in request.files:
        audio_file = request.files['audio']
        # Save temp audio for analysis
        tmp_audio_path = os.path.join(config.PROJECT_ROOT, "temp_stream.wav")
        audio_file.save(tmp_audio_path)
        try:
            gunshot_detected, gunshot_prob = detect_gunshot(tmp_audio_path)
            if gunshot_detected:
                STATS["gunshots"] += 1
        finally:
            if os.path.exists(tmp_audio_path):
                try:
                    os.remove(tmp_audio_path)
                except Exception:
                    pass

    # Multi-modal fusion
    multimodal = fuse_multimodal_threat(
        vision_events=threat_events,
        gunshot_detected=gunshot_detected,
        gunshot_prob=gunshot_prob
    )
    decision = multimodal["decision"]

    if "ARMED" in decision:
        STATS["armed_poachers"] += 1
    elif "RANGER" in decision:
        STATS["rangers"] += 1
    STATS["total"] += 1

    if multimodal["requires_immediate_dispatch"]:
        if 'image' in request.files:
            img_file = request.files['image']
            img_file.seek(0)
            saved_path = save_evidence(img_file)
            evidence_file = os.path.basename(saved_path) if saved_path else None

        generate_map(lat, lon)
        message = (
            f"🚨 MULTI-MODAL POACHING ALERT: {decision}\n"
            f"Urgency: {multimodal['urgency']} (Score: {multimodal['fused_score']*100:.1f}%)\n"
            f"Location: {lat}, {lon}\n"
            f"{multimodal['summary']}"
        )
        send_sms(message)

    event_entry = {
        "id": len(EVENT_HISTORY) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "decision": decision,
        "urgency": multimodal["urgency"],
        "fused_score": multimodal["fused_score"],
        "summary": multimodal["summary"],
        "latitude": lat,
        "longitude": lon,
        "detections_count": len(detections),
        "threat_events": threat_events,
        "evidence_file": evidence_file,
        "audio_gunshot": gunshot_detected
    }
    EVENT_HISTORY.append(event_entry)

    return jsonify({
        "decision": decision,
        "urgency": multimodal["urgency"],
        "fused_score": multimodal["fused_score"],
        "summary": multimodal["summary"],
        "threat_events": threat_events,
        "audio_gunshot_detected": gunshot_detected,
        "audio_gunshot_probability": gunshot_prob,
        "latitude": lat,
        "longitude": lon,
        "evidence_saved": bool(evidence_file)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.SERVER_PORT)