import flask
from flask import jsonify

from coma2.settings import DATABASE_URI, app, db

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route("/api/add-ingredient", methods=["POST"])
def add_ingredient():

    if __name__ == "__main__":
        app.run(debug=True)
