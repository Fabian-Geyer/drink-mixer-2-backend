from flask import jsonify, request, abort
from coma2.models.ingredients import Ingredients

from coma2.settings import app, db
import coma2.constants as c


@app.route("/api/ingredients", methods=["POST", "GET"])
def handle_ingredient():
    if request.method == "POST":
        ingred_name = request.get_json()["name"]
        # check for duplicates
        duplicate = Ingredients.query.filter_by(name=ingred_name).first()
        print("duplicate:: " + str(duplicate))
        if not duplicate:
            alcohol_percentage = request.get_json()["alcohol_percentage"]
            ingredient = Ingredients(
                name=ingred_name, alcohol_percentage=alcohol_percentage)
            db.session.add(ingredient)
            db.session.commit()
            return jsonify(ingredient.serialize)
        else:
            return abort(400, "This Ingredient name already exists")
    if request.method == "GET":
        return jsonify([elem.serialize for elem in Ingredients.query.all().order_by()])
        #TODO: allow filtering by alcohol etc.

    if __name__ == "__main__":
        app.run(c.DEBUG)
