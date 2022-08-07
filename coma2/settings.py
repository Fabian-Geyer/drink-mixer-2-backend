import os
from flask import Flask
from dotenv import find_dotenv, load_dotenv
from flask_sqlalchemy import SQLAlchemy

# constants
DATABASE_URI = os.environ.get("DATABASE_PATH")


# init Flask app and SQLAlchemy database object
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)