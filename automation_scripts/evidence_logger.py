# evidence_logger.py

import os
from datetime import datetime

def save_evidence(image):

    if not os.path.exists("evidence"):
        os.makedirs("evidence")

    filename = f"evidence/evidence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    image.save(filename)