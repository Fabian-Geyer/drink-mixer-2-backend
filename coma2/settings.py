import os
from flask import Flask
from dotenv import find_dotenv, load_dotenv
from flaskext.mysql import MySQL

# constants
DATABASE_URI = os.environ.get("DATABASE_PATH")


# init app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# MySQL init
db = MySQL()
db.init_app(app)
