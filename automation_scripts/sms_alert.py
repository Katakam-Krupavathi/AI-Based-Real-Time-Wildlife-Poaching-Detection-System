# sms_alert.py

from twilio.rest import Client
import config

def send_sms(message):
    client = Client(config.TWILIO_SID, config.TWILIO_TOKEN)

    client.messages.create(
        body=message,
        from_=config.TWILIO_FROM,
        to=config.TWILIO_TO
    )
