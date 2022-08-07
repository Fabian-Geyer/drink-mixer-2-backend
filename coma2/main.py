import flask
from flask import jsonify, request
from coma2.models.ingredients import Ingredients

from coma2.settings import app, db
import coma2.constants as c


@app.route("/api/ingredient", methods=["POST"])
def handle_ingredient():
    if request.method == "POST":
        name = request.get_json()["name"]
        alcohol_percentage = request.get_json()["alcohol_percentage"]
        ingredient = Ingredients(
            name=name, alcohol_percentage=alcohol_percentage)
        db.session.add(ingredient)
        db.session.commit()
        return jsonify(ingredient.serialize)

    if __name__ == "__main__":
        app.run(c.DEBUG)
