from pymongo import MongoClient
import hashlib
import os
from flask import request, jsonify

mongo_client = MongoClient("mongo")
db = mongo_client["CLUELESS"]
userDB = db["users"]

def validate_password(password):
    specialChar = {'!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '='}
    validChar = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&()-_=')
    if len(password) < 8:
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char in specialChar for char in password):
        return False
    if not all(char in validChar for char in password):
        return False
    return True

def register():
    username = request.form.get('username')
    password = request.form.get('password')
    repeatPassword = request.form.get("repeat password")
    
    if userDB.find_one({"username": username}):
        return jsonify({"message": "Username already exists"}), 400

    if repeatPassword == password and validate_password(password):
        salt = os.urandom(16)
        salted_password = password.encode() + salt
        hashed_password = hashlib.sha256(salted_password).hexdigest()

        user_info = {
            "username": username,
            "password": hashed_password,
            "salt": salt.hex()
        }
        userDB.insert_one(user_info)

    return jsonify({"message": "User registered successfully"}), 200