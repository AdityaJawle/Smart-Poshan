from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
from app import db
import uuid
class User:

    def start_session(self, user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        return jsonify(user), 200



    # Signup form
    def signup(self):
        print(request.form)

        # Create username
        user = {
            "_id": uuid.uuid4().hex,
            "name": request.form.get('name'),
            "school": request.form.get('school'),
            "email": request.form.get('email'),
            "password": request.form.get('password'),
            "state": request.form.get('state'),
            "district": request.form.get('district')
        }

        # Encrypt passwrd

        user['password'] = pbkdf2_sha256.encrypt(user['password'])

        # check if the email already exists
        if db.users.find_one({"email" : user['email']}):
            return jsonify({"error" : "Error Email already in use"}), 400

        if db.users.insert_one(user):
            return self.start_session(user)
    
    # Admin Signup form
    def adsignup(self):
        print(request.form)

        # Create username
        user = {
            "_id": uuid.uuid4().hex,
            "name": request.form.get('name'),
            "username": request.form.get('username'),
            "email": request.form.get('email'),
            "password": request.form.get('password'),
            "state": request.form.get('state'),
            "district": request.form.get('district')
        }

        # Encrypt passwrd

        user['password'] = pbkdf2_sha256.encrypt(user['password'])

        # check the email already exist

        if db.admin.find_one({"email" : user['email']}):
            return jsonify({"error" : "Error Email already in use"}), 400

        if db.admin.insert_one(user):
            return self.start_session(user)

        return jsonify({"error" : "Signup failed"}), 400
    
    def signout(self):
        session.clear()
        return redirect('/')
    
    def login(self):

        user = db.users.find_one({
            "email": request.form.get('email')
        })

        if user and pbkdf2_sha256.verify(request.form.get('password'),  (user['password'])):
            return self.start_session(user)
        
        return jsonify({"error" : "Invaild Login Credentials"}), 401
    
    def admin(self):

        user = db.admin.find_one({
            "email": request.form.get('email')
        })

        if user and pbkdf2_sha256.verify(request.form.get('password'),  (user['password'])):
            return self.start_session(user)
        
        return jsonify({"error" : "Invaild Login Credentials"}), 401
    