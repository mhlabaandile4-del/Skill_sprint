import jwt
import datetime
import os
from functools import wraps
import streamlit as st
from config import require_setting

SECRET_KEY = require_setting("JWT_SECRET_KEY")

def create_jwt_token(user_id, email, role):
    """
    Generate JWT token with user information
    Token expires in 24 hours
    """
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def verify_jwt_token(token):
    """
    Verify and decode JWT token
    Returns payload if valid, None if expired or invalid
    """
    try:
        if not token:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None
    except Exception as e:
        print(f"Token verification error: {e}")
        return None

def require_auth(func):
    """
    Decorator to protect pages
    Checks if JWT token exists and is valid
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = st.session_state.get('jwt_token')
        if not token or not verify_jwt_token(token):
            st.error("❌ Unauthorized. Please login.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper

def is_token_valid():
    """
    Check if current session has valid JWT token
    """
    token = st.session_state.get('jwt_token')
    return token is not None and verify_jwt_token(token) is not None

def get_user_from_token():
    """
    Extract user info from JWT token
    """
    token = st.session_state.get('jwt_token')
    if token:
        payload = verify_jwt_token(token)
        if payload:
            return {
                'user_id': payload.get('user_id'),
                'email': payload.get('email'),
                'role': payload.get('role')
            }
    return None