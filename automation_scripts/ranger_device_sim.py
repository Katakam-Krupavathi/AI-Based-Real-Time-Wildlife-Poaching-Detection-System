import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import hashlib
import config

def ranger_response(challenge):

    entered_code = input("Enter today's ranger passcode: ")

    raw = challenge + entered_code + config.LORA_SECRET_KEY
    response_hash = hashlib.sha256(raw.encode()).hexdigest()

    return response_hash