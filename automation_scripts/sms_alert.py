# sms_alert.py

import logging
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SMSAlert")

def send_sms(message):
    """
    Sends an SMS alert via Twilio, or logs the alert message if Twilio credentials are not configured.
    """
    sid = getattr(config, "TWILIO_SID", "")
    token = getattr(config, "TWILIO_TOKEN", "")
    from_num = getattr(config, "TWILIO_FROM", "")
    to_num = getattr(config, "TWILIO_TO", "")

    has_valid_credentials = bool(
        sid and token and from_num and to_num
        and not sid.startswith("your_")
        and not token.startswith("your_")
    )

    if not has_valid_credentials:
        logger.info(f"[SMS SIMULATION / MOCK] Alert dispatched:\n{message}")
        return False

    try:
        from twilio.rest import Client
        client = Client(sid, token)
        msg = client.messages.create(
            body=message,
            from_=from_num,
            to=to_num
        )
        logger.info(f"SMS alert sent successfully (SID: {msg.sid})")
        return True
    except Exception as e:
        logger.error(f"Failed to send Twilio SMS: {e}")
        return False
