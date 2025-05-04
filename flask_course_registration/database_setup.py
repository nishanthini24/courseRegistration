from pymongo import MongoClient
from werkzeug.security import generate_password_hash

client = MongoClient("mongodb://localhost:27017/")
db = client['course_registration']
students_collection = db['students']
admin_collection = db['admins']

admin_user = {
    "username": "admin",
    "password": generate_password_hash("admin123")  # Change password
}

db.admins.insert_one(admin_user)
print("Admin created successfully")
