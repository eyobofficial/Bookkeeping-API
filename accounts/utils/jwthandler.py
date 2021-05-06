from accounts.serializers import UserSerializer


def jwt_response_payload_handler(token, user=None, request=None):
    """
    Return serialized user data along with JWT token
    """
    tokens = {
        'refresh': str(token),
        'access': str(token.access_token)
    }
    serializer = UserRegistrationSerializer(user, context={'request': request})
    data = serializer.data
    data.update(tokens=tokens)
    return data
