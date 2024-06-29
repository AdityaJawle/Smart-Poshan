from flask import Flask, session, redirect, request, jsonify
from flask import render_template
from functools import wraps
import pymongo
from flask_cors import CORS
from bson import json_util
from datetime import datetime
import base64



app = Flask(__name__)
app.debug = True
CORS(app)
app.secret_key = b'\xb0\xac\xad\xe7\xd7^\xba2\x8f:\xe9\xe6\xf4\xe6t\xe6'
# Database
client = pymongo.MongoClient('localhost', 27017)
db = client.smart_poshan



# Decorators
def login_required(f):
    @wraps(f)
    def wrap(*args , **kwargs):
        if 'logged_in' in session:
            return f(*args , **kwargs)
        else:
            return redirect('/')
    return wrap


# Routes
from user import controller
from user import models
from admin import controller
from admin import models
from user.controller import process_image_upload, fetch_nutritional_info, nutritional_data
@app.route("/")
def home():
    return render_template('index.html')

@app.route("/adashboard/")
@login_required 
def adashboard():
    return render_template('adashboard.html')

@app.route("/dashboard/")
@login_required 
def dashboard():
    return render_template('dashboard.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    uploaded_image_path = None
    food_item = None
    calories = None
    protein = None
    image_data = None
    
    if request.method == 'POST':
        uploaded_file = request.files['file']
        food_item, calories, protein, uploaded_image_path, image_data = process_image_upload(uploaded_file, nutritional_data)

    return render_template('dashboard.html', uploaded_image_path=uploaded_image_path,
                           food_item=food_item, calories=calories, protein=protein,
                           image_data=image_data)


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)
