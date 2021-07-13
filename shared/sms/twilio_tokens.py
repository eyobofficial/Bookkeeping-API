from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from django.conf import settings


class TwilioTokenService:
    """
    Implement OTP verification using the Twilio Verify service.
    Documentation: https://www.twilio.com/docs/verify/api
    """

    SERVICE_NAME = 'Dukka'

    def __init__(self, to, service_id=None, *args, **kwargs):
        twilio_account_sid = settings.TWILIO_ACCOUNT_SID
        twilio_auth_token = settings.TWILIO_AUTH_TOKEN
        self.to = to
        self.client = Client(twilio_account_sid, twilio_auth_token)
        self.verification = None
        self.verification_check = None

        # Create Twilio verification service
        self.service = self._get_service(service_id)

    def _get_service(self, service_id=None):
        try:
            return self.client.verify.services(service_id).fetch()
        except TwilioRestException:
            return self.client.verify.services.create(
                friendly_name=TwilioTokenService.SERVICE_NAME
            )

    @property
    def service_id(self):
        return self.service.sid

    def send_verification(self):
        try:
            self.verification = self.client.verify.services(
                self.service_id
            ).verifications.create(to=self.to, channel='sms')
            return self.verification.status
        except TwilioRestException as e:
            print(e)
            raise

    def check_verification(self, code):
        try:
            self.verification_check = self.client.verify.services(
                self.service_id
            ).verification_checks.create(to=self.to, code=code)
            return True if self.verification_check.status == 'approved' else False
        except TwilioRestException as e:
            print(e)
            raise

