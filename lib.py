import pyrebase
import jwt
from auth import create_jwt_token, verify_jwt_token

# FIREBASE CONFIGURATION
firebaseConfig = {
    'apiKey': "AIzaSyD1tM5MWpg09sYYYAX0IO8ifdp7QG-SYUA",
    'authDomain': "skillsprint-cf16f.firebaseapp.com",
    'databaseURL': "https://skillsprint-cf16f-default-rtdb.europe-west1.firebasedatabase.app/",
    'projectId': "skillsprint-cf16f",
    'storageBucket': "skillsprint-cf16f.firebasestorage.app",
    'messagingSenderId': "137896376970",
    'appId': "1:137896376970:web:6cf8b0d255e2981c100b73",
    'measurementId': "G-92Y6Y9J966"
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