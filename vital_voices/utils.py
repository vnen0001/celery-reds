import jwt
from  datetime import timedelta,datetime
from django.conf import settings
import os
import subprocess

def generate_token(user_id):
    payload={
        'user_id':user_id,
        'expiry':datetime.utcnow()+ timedelta(days=1)
    }

    return jwt.encode(payload,settings.SECRET_KEY,algorithm='HS256')
def verify_token(token):
    try:    
        payload =jwt.decode(token,settings.SECRET_KEY,algorithm='HS256')
        return payload['user_id']
    except Exception as e:
        return('Except as ',str(e))
    
def find_ffmpeg():
    try:
        # For Unix-like systems (Linux, macOS)
        path = subprocess.check_output(["which", "ffmpeg"]).decode().strip()
    except subprocess.CalledProcessError:
        try:
            # For Windows
            path = subprocess.check_output(["where", "ffmpeg"]).decode().strip()
        except subprocess.CalledProcessError:
            # If ffmpeg is not found in PATH
            path = None
    
    return path

