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
    detections format:
    [
        {"label": "human", "center": (x,y), "conf": 0.87, "box": [x1, y1, x2, y2]},
        {"label": "gun", "center": (x,y), "conf": 0.61, "box": [x1, y1, x2, y2]},
        {"label": "jacket", "center": (x,y), "conf": 0.92, "box": [x1, y1, x2, y2]}
    ]
    """
    humans = []
    jackets = []
    guns = []

    # Separate detections by class
    for d in detections:
        label = d.get("label", "")
        if label == "human":
            humans.append(d)
        elif label == "jacket":
            jackets.append(d)
        elif label == "gun":
            guns.append(d)

    events = []

    # Analyze each detected human
    for human in humans:
        is_ranger = False
        is_armed = False

        # Check if human is wearing a ranger jacket
        for jacket in jackets:
            if is_proximate(human, jacket, BBOX_PROXIMITY_PX):
                is_ranger = True
                break

        # Check if human has a gun
        for gun in guns:
            if is_proximate(human, gun, BBOX_PROXIMITY_PX):
                is_armed = True
                break

        h_loc = human["center"] if isinstance(human, dict) else human

        # Determine event type
        if is_ranger:
            events.append({
                "type": "RANGER",
                "confidence": "LOW",
                "location": h_loc
            })
        elif is_armed:
            events.append({
                "type": "ARMED_POACHER",
                "confidence": "HIGH",
                "location": h_loc
            })
        else:
            events.append({
                "type": "POACHER_EVENT",
                "confidence": "MEDIUM",
                "location": h_loc
            })

    return events