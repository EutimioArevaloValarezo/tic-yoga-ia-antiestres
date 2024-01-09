from flask import *
from app import app

@app.route('/')
def home():
    try:
        return render_template('home.html')
    except Exception as e:
        return e