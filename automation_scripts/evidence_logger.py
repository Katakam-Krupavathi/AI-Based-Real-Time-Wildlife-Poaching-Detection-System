# evidence_logger.py

import os
import shutil
from datetime import datetime
import config

def save_evidence(image):
    """
    Saves an evidence image (FileStorage, numpy ndarray, PIL Image, or file path)
    into the evidence directory.
    """
    evidence_dir = os.path.join(config.PROJECT_ROOT, "evidence")
    os.makedirs(evidence_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = os.path.join(evidence_dir, f"evidence_{timestamp}.jpg")

    if hasattr(image, "save"):
        # Flask FileStorage or PIL Image
        image.save(filename)
    elif isinstance(image, str) and os.path.exists(image):
        shutil.copyfile(image, filename)
    else:
        # Assume numpy ndarray (OpenCV image)
        try:
            import cv2
            cv2.imwrite(filename, image)
        except Exception as e:
            print(f"Warning: Failed to save evidence array: {e}")

    return filename