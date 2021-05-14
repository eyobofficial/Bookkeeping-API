"""
One-time Password (OTP) Generator Module.
"""

import math
import random
import string


def generate_otp():
    """
    Returns a 6 digit numeric only one-time password.

    Returns:
      otp (str): 6-digit numeric only string
    """
    otp = []

    for i in range(6):
        index = random.randint(0, 9)
        digit = string.digits[index]
        otp.append(digit)

    return ''.join(otp)
