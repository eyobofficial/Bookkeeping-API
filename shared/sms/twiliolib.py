"""
Send SMS via Twilio Serivce.
"""
from django.conf import settings

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client


def send_sms(to, message):
    twilio_sid = settings.TWILIO_ACCOUNT_SID
    twilio_auth = settings.TWILIO_AUTH_TOKEN
    twilio_phone_number = settings.TWILIO_PHONE_NUMBER

    # Initilize client
    client = Client(twilio_sid, twilio_auth)

    try:
        message = client.messages.create(
            to=to,
            from_=twilio_phone_number,
            body=message
        )
    except TwilioRestException as e:
        print(e)
