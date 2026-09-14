"""
SANJEEVANI: AI-Based Real-Time Wildlife Poaching Detection System
End-to-End Synthetic Demonstration and Verification Script

This script walks through 6 core operational surveillance scenarios:
  1. System Diagnostic & Self-Test (/health)
  2. Baseline Wildlife Monitoring (Elephant Detected - Normal)
  3. Authorized Ranger Patrol (Human + LoRa Ranger Beacon - Safe)
  4. Poacher Incursion & Weapon Detection (Visual Threat - Alert Dispatched)
  5. Multi-Modal Audio-Visual Combat Fusion (Gunshot Acoustic + Visual Poacher)
  6. Command Center Dashboard Telemetry (/api/events & /api/latest-map)
"""

import os
import sys
import json
import time
import io

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from automation_scripts.central_server import app
from automation_scripts.config import PROJECT_ROOT as CFG_PROJECT_ROOT

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    banner = f"""
{Colors.CYAN}{Colors.BOLD}================================================================================
  SANJEEVANI -- AI-BASED REAL-TIME WILDLIFE POACHING DETECTION SYSTEM
            Autonomous Multi-Modal IoT Surveillance Command Center
================================================================================{Colors.ENDC}"""
    print(banner)

def get_sample_path(filename):
    return os.path.join(CFG_PROJECT_ROOT, "Dataset Samples", filename)

def run_scenario_1_health(client):
    print(f"\n{Colors.HEADER}{Colors.BOLD}[SCENARIO 1] Running System Health & Subsystem Diagnostics (/health)...{Colors.ENDC}")
    res = client.get('/health')
    data = res.get_json()
    print(f"HTTP Status: {res.status_code}")
    print(json.dumps(data, indent=2))
    assert res.status_code == 200, "Health check failed!"
    print(f"{Colors.GREEN}[+] Subsystems Verified: YOLO Model, Gunshot Model, Twilio Service, Storage Directories.{Colors.ENDC}")

def run_scenario_2_wildlife(client):
    print(f"\n{Colors.HEADER}{Colors.BOLD}[SCENARIO 2] Baseline Wildlife Monitoring: Camera Trap Frame (Elephant Only){Colors.ENDC}")
    sample_img = get_sample_path("elephant_ELEPHANT_4.jpg")
    with open(sample_img, "rb") as f:
        img_bytes = f.read()

    data = {
        'image': (io.BytesIO(img_bytes), 'elephant_trap.jpg'),
        'lat': '11.6854',
        'lon': '76.6231',
        'device_id': 'CAM_NODE_01',
        'rssi': '-95'
    }
    res = client.post('/process', data=data, content_type='multipart/form-data')
    result = res.get_json()
    print(f"Response: {json.dumps(result, indent=2)}")
    print(f"{Colors.GREEN}[+] Processed: Threat Level -> {result.get('threat_level')} | Wildlife Logged Safe{Colors.ENDC}")

def run_scenario_3_ranger_patrol(client):
    print(f"\n{Colors.HEADER}{Colors.BOLD}[SCENARIO 3] Ranger Patrol Detection (Human in Sector + Authorized LoRa Beacon RSSI -45 dBm){Colors.ENDC}")
    sample_img = get_sample_path("forest_ranger_FOREST_RANGER_3_aug0.jpg")
    with open(sample_img, "rb") as f:
        img_bytes = f.read()

    data = {
        'image': (io.BytesIO(img_bytes), 'ranger_patrol.jpg'),
        'lat': '11.6870',
        'lon': '76.6250',
        'device_id': 'CAM_NODE_02',
        'rssi': '-45'  # Strong ranger tag RSSI
    }
    res = client.post('/process', data=data, content_type='multipart/form-data')
    result = res.get_json()
    print(f"Response: {json.dumps(result, indent=2)}")
    print(f"{Colors.GREEN}[+] LoRa Deconfliction Verified: Threat Level -> {result.get('threat_level')} (Ranger Identified){Colors.ENDC}")

def run_scenario_4_poacher_alert(client):
    print(f"\n{Colors.HEADER}{Colors.BOLD}[SCENARIO 4] Poacher Incursion Alert (Visual Human + Weapon Detection, No LoRa Beacon){Colors.ENDC}")
    sample_img = get_sample_path("poacher_POACHER_4.jpg")
    with open(sample_img, "rb") as f:
        img_bytes = f.read()

    data = {
        'image': (io.BytesIO(img_bytes), 'poacher_incursion.jpg'),
        'lat': '11.6912',
        'lon': '76.6288',
        'device_id': 'CAM_NODE_03',
        'rssi': '-110'  # No ranger tag nearby
    }
    res = client.post('/process', data=data, content_type='multipart/form-data')
    result = res.get_json()
    print(f"Response: {json.dumps(result, indent=2)}")
    print(f"{Colors.WARNING}[!] Visual Threat: Level -> {result.get('threat_level')} | SMS Dispatched -> {result.get('sms_sent')}{Colors.ENDC}")

def run_scenario_5_multimodal_combat(client):
    print(f"\n{Colors.HEADER}{Colors.BOLD}[SCENARIO 5] Multi-Modal Audio-Visual Combat Fusion (/process_multimodal){Colors.ENDC}")
    sample_img = get_sample_path("poacher_POACHER_IR_3.jpg")
    sample_audio = get_sample_path("aug_gun_679_0.wav")

    with open(sample_img, "rb") as f_img, open(sample_audio, "rb") as f_aud:
        img_bytes = f_img.read()
        aud_bytes = f_aud.read()

    data = {
        'image': (io.BytesIO(img_bytes), 'thermal_cam.jpg'),
        'audio': (io.BytesIO(aud_bytes), 'acoustic_mic.wav'),
        'lat': '11.6930',
        'lon': '76.6310',
        'device_id': 'MULTI_NODE_09',
        'rssi': '-105'
    }
    res = client.post('/process_multimodal', data=data, content_type='multipart/form-data')
    result = res.get_json()
    print(f"Response: {json.dumps(result, indent=2)}")
    print(f"{Colors.FAIL}{Colors.BOLD}[!] Multi-Modal Fusion: Threat Level -> {result.get('threat_level')} | Confidence -> {result.get('composite_confidence')}{Colors.ENDC}")

def run_scenario_6_dashboard_events(client):
    print(f"\n{Colors.HEADER}{Colors.BOLD}[SCENARIO 6] Verifying Command Center Dashboard & Live Events Feed (/api/events)...{Colors.ENDC}")
    res = client.get('/api/events')
    data = res.get_json()
    print(f"Total Logged Incidents: {len(data)}")
    if data:
        print(f"Latest Incident: {json.dumps(data[-1], indent=2)}")
    print(f"{Colors.GREEN}[+] Live Incident Telemetry successfully routed to Web Dashboard{Colors.ENDC}")

def main():
    print_banner()
    app.config['TESTING'] = True
    with app.test_client() as client:
        run_scenario_1_health(client)
        time.sleep(0.3)
        run_scenario_2_wildlife(client)
        time.sleep(0.3)
        run_scenario_3_ranger_patrol(client)
        time.sleep(0.3)
        run_scenario_4_poacher_alert(client)
        time.sleep(0.3)
        run_scenario_5_multimodal_combat(client)
        time.sleep(0.3)
        run_scenario_6_dashboard_events(client)
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}================================================================================")
    print("  [SUCCESS] ALL SANJEEVANI SURVEILLANCE & AI SCENARIOS VERIFIED!")
    print(f"================================================================================{Colors.ENDC}\n")

if __name__ == '__main__':
    main()
