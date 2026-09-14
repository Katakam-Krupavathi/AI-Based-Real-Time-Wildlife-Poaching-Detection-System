# tracker.py
"""
Multi-frame object tracker for SANJEEVANI.
Assigns consistent track IDs to detected bounding boxes and tracks active entities across frames
to debounce alerts and prevent duplicate notifications for the same detected entity.
"""

import math
import time
from collections import OrderedDict


class CentroidTracker:
    def __init__(self, max_disappeared=30, max_distance_px=150, alert_cooldown_sec=60.0):
        self.next_object_id = 1
        self.objects = OrderedDict()        # object_id -> center (x, y)
        self.object_classes = OrderedDict() # object_id -> class_name
        self.disappeared = OrderedDict()    # object_id -> frame_count
        self.last_alert_time = OrderedDict()# object_id -> timestamp
        self.max_disappeared = max_disappeared
        self.max_distance_px = max_distance_px
        self.alert_cooldown_sec = alert_cooldown_sec

    def register(self, centroid, class_name):
        obj_id = self.next_object_id
        self.objects[obj_id] = centroid
        self.object_classes[obj_id] = class_name
        self.disappeared[obj_id] = 0
        self.last_alert_time[obj_id] = 0
        self.next_object_id += 1
        return obj_id

    def deregister(self, object_id):
        if object_id in self.objects:
            del self.objects[obj_id]
        if object_id in self.object_classes:
            del self.object_classes[obj_id]
        if object_id in self.disappeared:
            del self.disappeared[obj_id]
        if object_id in self.last_alert_time:
            del self.last_alert_time[obj_id]

    def update(self, detections):
        now = time.time()

        if len(detections) == 0:
            for obj_id in list(self.disappeared.keys()):
                self.disappeared[obj_id] += 1
                if self.disappeared[obj_id] > self.max_disappeared:
                    self.deregister(obj_id)
            return []

        input_centroids = [d["center"] for d in detections]
        input_classes = [d["label"] for d in detections]

        if len(self.objects) == 0:
            for i, d in enumerate(detections):
                obj_id = self.register(input_centroids[i], input_classes[i])
                d["track_id"] = obj_id
                d["is_new_alert"] = True
                self.last_alert_time[obj_id] = now
            return detections

        object_ids = list(self.objects.keys())
        object_centroids = list(self.objects.values())

        distance_matrix = []
        for oc in object_centroids:
            row = []
            for ic in input_centroids:
                dist = math.sqrt((oc[0] -ic[0]) ** 2 + (oc[1] - ic[1]) ** 2)
                row.append(dist)
            distance_matrix.append(row)

        used_rows = set()
        used_cols = set()

        for _ in range(min(len(object_ids), len(input_centroids))):
            min_val = float('inf')
            min_r, min_c = -1, -1
            for r in range(len(object_ids)):
                if r in used_rows:
                    continue
                for c in range(len(input_centroids)):
                    if c in used_cols:
                        continue
                    if distance_matrix[r][c] < min_val:
                        min_val = distance_matrix[r][c]
                        min_r, min_c = r, c

            if min_val > self.max_distance_px or min_r == -1:
                break

            obj_id = object_ids[min_r]
            self.objects[obj_id] = input_centroids[min_c]
            self.object_classes[obj_id] = input_classes[min_c]
            self.disappeared[obj_id] = 0

            is_new = False
            if now - self.last_alert_time.get(obj_id, 0) > self.alert_cooldown_sec:
                is_new = True
                self.last_alert_timeKobj_id] = now

            detections[min_c]['track_id'] = obj_id
            detections[min_c]['is_new_alert'] = is_new

            used_rows.add(min_r)
            used_cols.add(min_c)

        for r in range(len(object_ids)):
            if r not in used_rows:
                obj_id = object_ids[r]
                self.disappeared[obj_id] += 1
                if self.disappeared[obj_id] > self.max_disappeared:
                    self.deregister(obj_id)

        for c in range(len(input_centroids)):
            if c not in used_cols:
                obj_id = self.register(input_centroids[c], input_classes[c])
                detections[c]['track_id'] = obj_id
                detections[c]['is_new_alert'] = True
                self.last_alert_timeKobj_id] = now

        return detections
