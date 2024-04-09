from os import environ
import jwt

import bcrypt
from flask import request
from functools import wraps


def encrypt(password):
    if password == "":
        return ""
    return bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt())


def check_password(input, saved_password):
    if saved_password == "" and input == "":
        return True
    return bcrypt.checkpw(input.encode('UTF-8'), saved_password)


JWT_PASSWORD = environ.get('JWT_PASSWORD')


def encode_token(param):
    return jwt.encode(param, JWT_PASSWORD, algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, JWT_PASSWORD, algorithms=["HS256"])


def verify_token(token):
    if token is None:
        return False, ""
    token = decode_token(token)
    uid = token['uid']
    return True, uid

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        uid = ""
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            if not token:
                return {'error': 'unauthorized', 'description': 'token missing'}, 401
            try:
                authorized, uid = verify_token(token.replace('Bearer ', ''))
                if not authorized:
                    return {'error': 'unauthorized', 'description': 'user not registered'}, 401
            except:
                return {'error': 'unauthorized', 'description': 'token invalid'}, 401
        else:
            return {'error': 'unauthorized', 'description': 'token missing'}, 401
        return f(uid, *args, **kwargs)

    return decorator