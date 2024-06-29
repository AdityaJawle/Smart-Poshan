
from flask import Flask, render_template, request, redirect, url_for, jsonify
from .models import session
import random
import csv
import datetime
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
import hashlib
from pymongo import MongoClient
from app import db


def get_username_name():
    # Replace this with your actual implementation to get the logged-in school
    return session['user']['username']

def get_school_name():
    # Replace this with your actual implementation to get the logged-in school
    return session['user']['school']



def get_last_used_idno(school_name):
    school_name = get_school_name()
    csv_file = f'{school_name}_id_cards.csv'
    if os.path.exists(csv_file):
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            if rows:
                last_row = rows[-1]
                return int(last_row['ID'])
    return 0  # Default if no CSV file or empty

def generate_next_idno(school_name):
    last_used_idno = get_last_used_idno(school_name)
    return last_used_idno + 1

def calculate_sha_key(idno, name, school_name):
    unique_identifier = f"{idno}-{name}-{school_name}"
    sha_key = hashlib.sha256(unique_identifier.encode()).hexdigest()
    return sha_key

def save_to_csv(details, school_name):
    csv_file = f'{school_name}_id_cards.csv'
    fieldnames = ['ID', 'School Name', 'Roll No', 'Class', 'Name', 'SHAKey']

    if not os.path.exists(csv_file):
        with open(csv_file, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

    with open(csv_file, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(details)

def save_to_mongodb(details, school_name):
    sha_key = calculate_sha_key(details['ID'], details['Name'], school_name)
    details['SHAKey'] = sha_key
    db.id_cards.insert_one(details)

def save_png(image, name, school_name):
    png_directory = os.path.join(f'static/{school_name}_ID_Cards','png')

    # Create the directory if it doesn't exist
    if not os.path.exists(png_directory):
        os.makedirs(png_directory)

    png_file = os.path.join(png_directory, name + '.png')
    image.save(png_file)
    return png_file

def save_bmp(QR, idno, school_name):
    bmp_directory = os.path.join(f'static/{school_name}_ID_Cards', 'bmp')

    # Create the directory if it doesn't exist
    if not os.path.exists(bmp_directory):
        os.makedirs(bmp_directory)

    bmp_file = os.path.join(bmp_directory, str(idno) + '.bmp')
    QR.save(bmp_file)
    return bmp_file
