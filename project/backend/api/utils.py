from django.conf import settings
from io import BytesIO 
from rest_framework_simplejwt.tokens import RefreshToken
import base64
import pyotp
import qrcode

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'id': user.id,
        'username': user.username,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def get_auth_url(user):
    secret = user.otp_secret
    return  pyotp.TOTP(secret, interval=settings.OTP_INTERVAL).provisioning_uri(
        name=user.email,
        issuer_name='Pong',
    )

def get_image_b64(url):
    qr = qrcode.make(url)
    image = BytesIO()
    qr.save(image, 'PNG')
    return base64.b64encode(image.getvalue()).decode()