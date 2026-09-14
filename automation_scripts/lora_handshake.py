import hashlib
import random
import config

def generate_challenge():
    return str(random.randint(1000, 9999))

def create_expected_hash(challenge):
    raw = challenge + config.DAILY_PASSCODE + config.LORA_SECRET_KEY
    return hashlib.sha256(raw.encode()).hexdigest()

def verify_response(challenge, received_hash):
    expected = create_expected_hash(challenge)
    return expected == received_hash