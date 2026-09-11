import pyrebase
firebaseConfig = {'apiKey': "AIzaSyD1tM5MWpg09sYYYAX0IO8ifdp7QG-SYUA",
  'authDomain': "skillsprint-cf16f.firebaseapp.com",
  'databaseURL': "https://console.firebase.google.com/project/skillsprint-cf16f/database/skillsprint-cf16f-default-rtdb/data/~2F",
  'projectId': "skillsprint-cf16f",
  'storageBucket': "skillsprint-cf16f.firebasestorage.app",
  'messagingSenderId': "137896376970",
  'appId': "1:137896376970:web:6cf8b0d255e2981c100b73",
  'measurementId': "G-92Y6Y9J966"}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()


#STUDENT CLASS
class Student:
    def __init__(self, user_name, campus, email, password, short_bio, repo_link, rank):
        self.user_name = user_name
        self.campus    = campus
        self.email     = email
        self.password  = password
        self.short_bio = short_bio
        self.repo_link = repo_link
        self.rank      = rank
    
    
#STUDENT CLASS
#LECTURER CLASS   
class Lecturer:
    def __init__(self, user_name, campus, email, password, short_bio):
        self.user_name = user_name
        self.campus    = campus
        self.email     = email
        self.password  = password
        self.short_bio = short_bio


#LECTURER CLASS
#skillsprint-cf16f