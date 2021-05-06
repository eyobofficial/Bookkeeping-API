import africastalking

from django.conf import settings


class BaseSMS:
    """Base SMS class using the AfricanTalking library."""
    _MESSAGE = None
    _RECIPIENTS = []

    def __init__(self, *args, **kwargs):
        self.username = settings.AFRICASTALKING_USERNAME
        self.api_key = settings.AFRICASTALKING_API_KEY

        # Initialize the SDK
        africastalking.initialize(self.username, self.api_key)

        # Get the SMS service
        self.sms = africastalking.SMS

    @property
    def message(self):
        """
        Get message value.
        """
        return self._MESSAGE

    @message.setter
    def message(self, value):
        """
        Set message value.
        """
        self._MESSAGE = value

    @property
    def recipients(self):
        """
        Get a list of message recipients in international format.
        """
        return self._RECIPIENTS

    @recipients.setter
    def recipients(self, values):
        """
        Set a list of recipients in international format.
        """
        if isinstance(values, list):
            self._RECIPIENTS = values
        else:
            self._RECIPIENTS = [values]

    def _get_sender(self):
        """
        Return the senderId or the shortCode.
        """
        return settings.AFRICASTALKING_SENDER_ID

    def send(self):
        """
        Send the SMS message.
        """
        sender = self._get_sender()

        print('\n\n\n')
        print(f'Message: {self.message}')
        print(f'Recipients: {self.recipients}')
        print(f'Sender: {sender}')
        print('\n\n\n')

        try:
            response = self.sms.send(self.message, self.recipients, sender)
            print(response)
        except Exception as e:
            print(f'Encountered an error while sending: {str(e)}')
