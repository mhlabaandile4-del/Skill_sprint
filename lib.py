import pyrebase
import jwt
from auth import create_jwt_token, verify_jwt_token
from config import require_setting

# FIREBASE CONFIGURATION
firebaseConfig = {
    'apiKey': require_setting('FIREBASE_API_KEY'),
    'authDomain': require_setting('FIREBASE_AUTH_DOMAIN'),
    'databaseURL': require_setting('FIREBASE_DATABASE_URL'),
    'projectId': require_setting('FIREBASE_PROJECT_ID'),
    'storageBucket': require_setting('FIREBASE_STORAGE_BUCKET'),
    'messagingSenderId': require_setting('FIREBASE_MESSAGING_SENDER_ID'),
    'appId': require_setting('FIREBASE_APP_ID'),
    'measurementId': require_setting('FIREBASE_MEASUREMENT_ID')
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

# STUDENT CLASS
class Student:
    def __init__(self, user_name, campus, email, password, short_bio, repo_link, rank, role):
        self.user_name = user_name
        self.campus = campus
        self.email = email
        self.password = password
        self.short_bio = short_bio
        self.repo_link = repo_link
        self.rank = rank
        self.role = role

# LECTURER CLASS
class Lecturer:
    def __init__(self, user_name, campus, email, password, short_bio, role):
        self.user_name = user_name
        self.campus = campus
        self.email = email
        self.password = password
        self.short_bio = short_bio
        self.role = role

# ALUMNI CLASS
class Alumni:
    def __init__(self, user_name, campus, email, password, short_bio, role):
        self.user_name = user_name
        self.campus = campus
        self.email = email
        self.password = password
        self.short_bio = short_bio
        self.role = role

# ADMIN CLASS
class Admin:
    def __init__(self, user_name, email, password, role):
        self.user_name = user_name
        self.email = email
        self.password = password
        self.role = role

def create_jwt_on_login(user_id, email, role):
    """
    Create and return JWT token on successful login
    """
    return create_jwt_token(user_id, email, role)

def verify_admin_access(email):
    """
    Check if user email is in admin list
    """
    ADMIN_EMAILS = ["admin@skillsprint.com", "administrator@skillsprint.com"]
    return email in ADMIN_EMAILS