import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import math
from config import BBOX_PROXIMITY_PX


def distance(a, b):
    """
    Compute Euclidean distance between two points
    """
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


def is_proximate(human_item, other_item, threshold=BBOX_PROXIMITY_PX):
    """
    Check if other_item (jacket or gun) is associated with the human,
    checking center Euclidean distance and bounding box containment.
    """
    h_center = human_item["center"] if isinstance(human_item, dict) else human_item
    o_center = other_item["center"] if isinstance(other_item, dict) else other_item

    # Direct center-to-center Euclidean distance
    if distance(h_center, o_center) <= threshold:
        return True

    # If bounding box is available, check if other item center is within human bounds
    if isinstance(human_item, dict) and "box" in human_item:
        hx1, hy1, hx2, hy2 = human_item["box"]
        margin = threshold * 0.25
        if (hx1 - margin <= o_center[0] <= hx2 + margin) and (hy1 - margin <= o_center[1] <= hy2 + margin):
            return True

    return False


def analyze_detections(detections):
    """
    Analyzes visual detections and computes confidence-weighted threat signatures.
    """
    humans = []
    jackets = []
    guns = []

    for d in detections:
        label = d.get("label", "")
        if label == "human":
            humans.append(d)
        elif label == "jacket":
            jackets.append(d)
        elif label == "gun":
            guns.append(d)

    events = []

    for human in humans:
        is_ranger = False
        is_armed = False
        h_conf = human.get("conf", 0.8)
        ranger_conf = 0.0
        armed_conf = 0.0

        # Check if human is wearing a ranger jacket
        for jacket in jackets:
            if is_proximate(human, jacket, BBOX_PROXIMITY_PX):
                is_ranger = True
                ranger_conf = max(ranger_conf, jacket.get("conf", 0.8))
                break

        # Check if human has a gun
        for gun in guns:
            if is_proximate(human, gun, BBOX_PROXIMITY_PX):
                is_armed = True
                armed_conf = max(armed_conf, gun.get("conf", 0.8))
                break

        h_loc = human["center"] if isinstance(human, dict) else human
        track_id = human.get("track_id", None)
        is_new_alert = human.get("is_new_alert", True)

        if is_ranger:
            fused_conf = (h_conf + ranger_conf) / 2.0
            events.append({
                "type": "RANGER",
                "urgency": "INFO",
                "confidence_score": round(float(fused_conf), 4),
                "confidence_pct": f"{fused_conf * 100:.1f}%",
                "location": h_loc,
                "track_id": track_id,
                "is_new_alert": is_new_alert,
                "description": "Verified Forest Ranger Patrol"
            })
        elif is_armed:
            fused_conf = round(float(0.4 * h_conf + 0.6 * armed_conf), 4)
            events.append({
                "type": "ARMED_POACHER",
                "urgency": "CRITICAL",
                "confidence_score": fused_conf,
                "confidence_pct": f"{fused_conf * 100:.1f}%",
                "location": h_loc,
                "track_id": track_id,
                "is_new_alert": is_new_alert,
                "description": f"Armed Poacher Detected (Gun: {armed_conf*100:.1f}%, Human: {h_conf*100:.1f}%)"
            })
        else:
            fused_conf = round(float(h_conf), 4)
            events.append({
                "type": "POACHER_EVENT",
                "urgency": "HIGH",
                "confidence_score": fused_conf,
                "confidence_pct": f"{fused_conf * 100:.1f}%",
                "location": h_loc,
                "track_id": track_id,
                "is_new_alert": is_new_alert,
                "description": f"Unauthorized Human in Protected Zone (Conf: {h_conf*100:.1f}%)"
            })

    return events


def fuse_multimodal_threat(vision_events, gunshot_detected=False, gunshot_prob=0.0):
    """
    Combines visual object analysis and acoustic gunshot classifier into a unified
    multi-modal threat score and priority tier.
    """
    has_armed_poacher = any(e["type"] == "ARMED_POACHER" for e in vision_events)
    has_unarmed_poacher = any(e["type"] == "POACHER_EVENT" for e in vision_events)
    has_ranger = any(e["type"] == "RANGER" for e in vision_events)

    max_vis_conf = max([e.get("confidence_score", 0.0) for e in vision_events], default=0.0)

    if has_armed_poacher and gunshot_detected:
        # Fused multi-modal active combat / poaching incident
        fused_score = min(1.0, 0.5 * max_vis_conf + 0.5 * gunshot_prob + 0.1)
        return {
            "decision": "TIER_1_CRITICAL_ACTIVE_POACHING",
            "urgency": "CRITICAL",
            "fused_score": round(float(fused_score), 4),
            "summary": f"🚨 CRITICAL: Active Armed Poaching with Gunfire (Vision: {max_vis_conf*100:.1f}%, Audio: {gunshot_prob*100:.1f}%)",
            "requires_immediate_dispatch": True
        }
    elif has_armed_poacher:
        return {
            "decision": "TIER_2_ARMED_POACHER_VISUAL",
            "urgency": "HIGH",
            "fused_score": round(float(max_vis_conf), 4),
            "summary": f"⚠️ HIGH ALERT: Armed Poacher Sighted (Conf: {max_vis_conf*100:.1f}%)",
            "requires_immediate_dispatch": True
        }
    elif gunshot_detected:
        return {
            "decision": "TIER_2_ACOUSTIC_GUNSHOT_ALERT",
            "urgency": "HIGH",
            "fused_score": round(float(gunshot_prob), 4),
            "summary": f"🔊 HIGH ALERT: Acoustic Gunshot Detected (Acoustic Conf: {gunshot_prob*100:.1f}%)",
            "requires_immediate_dispatch": True
        }
    elif has_unarmed_poacher:
        return {
            "decision": "TIER_3_SUSPECTED_POACHER_INTRUSION",
            "urgency": "MEDIUM",
            "fused_score": round(float(max_vis_conf), 4),
            "summary": f"⚠️ ALERT: Unauthorized Intruder in Sanctuary (Conf: {max_vis_conf*100:.1f}%)",
            "requires_immediate_dispatch": True
        }
    elif has_ranger:
        return {
            "decision": "TIER_4_RANGER_PATROL_MONITORED",
            "urgency": "INFO",
            "fused_score": round(float(max_vis_conf), 4),
            "summary": f"🛡️ Ranger Patrol Verified (Conf: {max_vis_conf*100:.1f}%)",
            "requires_immediate_dispatch": False
        }
    else:
        return {
            "decision": "TIER_4_NO_THREAT",
            "urgency": "NONE",
            "fused_score": 0.0,
            "summary": "🌿 Sector Clear / Wildlife Normal",
            "requires_immediate_dispatch": False
        }