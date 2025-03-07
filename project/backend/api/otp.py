import pyotp
from django.conf import settings

def generate_otp(user):
    # Generate a TOTP object
    totp = pyotp.TOTP(user.otp_secret, interval=settings.OTP_INTERVAL)
    otp = totp.now()
    return otp

def verify_otp(user, otp):
    totp = pyotp.TOTP(user.otp_secret, interval=settings.OTP_INTERVAL)
    return totp.verify(otp)
