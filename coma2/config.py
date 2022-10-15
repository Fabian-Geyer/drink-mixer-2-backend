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

# add blueprints
from coma2.cocktails.routes import cocktails
from coma2.ingredients.routes import ingredients
from coma2.slots.routes import slots
from coma2.config import app
from coma2.docs.swagger import swaggerui_blueprint

app.register_blueprint(cocktails)
app.register_blueprint(slots)
app.register_blueprint(ingredients)
app.register_blueprint(swaggerui_blueprint)
