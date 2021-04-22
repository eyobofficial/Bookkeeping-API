from phonenumber_field.serializerfields import PhoneNumberField


class CustomPhoneNumberField(PhoneNumberField):
    """
    Custom phone number field with a JSON serializable representation.
    """

    def to_representation(self, value):
        return value.as_e164
