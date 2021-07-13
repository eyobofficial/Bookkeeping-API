import requests

from django.conf import settings


def send_termii_token():
    pass


class TermiiToken:
    ENDPOINT = 'https://termii.com/api/sms/otp/send'
    HEADERS = {'Content-Type': 'application/json'}

    def __init__(self, to):
        self.payload = {
            'api_key': settings.TERMII_API_KEY,
            'message_type': 'NUMERIC',
            'to': to,
            'from' : 'Aproved Sender or Device IDs',
            'channel': 'dnd',
            'pin_attempts': 10,
            'pin_time_to_live': 60,
            'pin_length': 6,
            'pin_placeholder': '< 1234 >',
            'message_text': 'Your OTP is < 1234 >',
            'pin_type': 'NUMERIC'
        }

    def send(self):
        """
        Sends a one-time password (OTP).

        Returns:
          The status of the Response object.

        Raises:
          4xx or 5xx exception when sending OTP failed.
        """
        response = requests.post(
            TermiiToken.ENDPOINT,
            data=self.payload,
            headers=TermiiToken.HEADERS
        )
        response.raise_for_status()
        print(response.text)
        return response.status_code






