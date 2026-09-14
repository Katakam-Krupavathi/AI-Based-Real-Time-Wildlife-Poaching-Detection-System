import math
from config import PROXIMITY_THRESHOLD


def distance(a, b):
    """
    Compute Euclidean distance between two points
    """
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)


def analyze_detections(detections):
    """
    detections format example:

    [
        {"label": "human", "center": (x,y), "conf":0.87},
        {"label": "gun", "center": (x,y), "conf":0.61},
        {"label": "jacket", "center": (x,y), "conf":0.92}
    ]
    """

    humans = []
    jackets = []
    guns = []

    # Separate detections by class
    for d in detections:

        label = d["label"]
        center = d["center"]

        if label == "human":
            humans.append(center)

        elif label == "jacket":
            jackets.append(center)

        elif label == "gun":
            guns.append(center)

    events = []

    # Analyze each human
    for human in humans:

        is_ranger = False
        is_armed = False

        # Check if human has jacket (ranger)
        for jacket in jackets:

            if distance(human, jacket) < PROXIMITY_THRESHOLD:
                is_ranger = True
                break

        # Check if human has gun
        for gun in guns:

            if distance(human, gun) < PROXIMITY_THRESHOLD:
                is_armed = True
                break

        # Determine event type
        if is_ranger:
            events.append({
                "type": "RANGER",
                "confidence": "LOW",
                "location": human
            })

        else:

            if is_armed:
                events.append({
                    "type": "ARMED_POACHER",
                    "confidence": "HIGH",
                    "location": human
                })

            else:
                events.append({
                    "type": "POACHER_EVENT",
                    "confidence": "MEDIUM",
                    "location": human
                })

    return events