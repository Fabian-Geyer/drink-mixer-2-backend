import flask
from flask import jsonify, request
from coma2.models.ingredients import Ingredients

from coma2.settings import app, db
import coma2.constants as c


@app.route("/api/ingredients", methods=["POST", "GET"])
def handle_ingredient():
    if request.method == "POST":
        name = request.get_json()["name"]
        alcohol_percentage = request.get_json()["alcohol_percentage"]
        ingredient = Ingredients(
            name=name, alcohol_percentage=alcohol_percentage)
        db.session.add(ingredient)
        db.session.commit()
        return jsonify(ingredient.serialize)
    if request.method == "GET":
        return jsonify([elem.serialize for elem in Ingredients.query.all().order_by()])
        #TODO: allow filtering by alcohol etc.

    if __name__ == "__main__":
        app.run(c.DEBUG)
