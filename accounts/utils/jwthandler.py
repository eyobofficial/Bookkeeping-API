from accounts.serializers import UserRegistrationSerializer


def jwt_response_payload_handler(token, user=None, request=None):
    """
    Return serialized user data along with JWT token
    """
    data = {'token': token}
    serializer = UserRegistrationSerializer(user, context={'request': request})
    data.update(serializer.data)
    return data
