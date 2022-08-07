from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import coma2.constants as c


# init Flask app and SQLAlchemy database object
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = c.DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)