from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_cors import CORS

import coma2.constants as c


# init Flask app and SQLAlchemy database object
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = c.DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)