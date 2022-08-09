from flask import jsonify, request, abort

from coma2.models.cocktails import Cocktail, Ingredient
from coma2.settings import app, db
import coma2.constants as c


@app.route("/api/ingredients", methods=["POST", "GET"])
def handle_ingredient():
    if request.method == "POST":
        ingred_name = request.get_json()["name"]
        # check for duplicates
        duplicate = Ingredient.query.filter_by(name=ingred_name).first()
        print("duplicate:: " + str(duplicate))
        if not duplicate:
            alcohol_percentage = request.get_json()["alcohol_percentage"]
            ingredient = Ingredient(
                name=ingred_name, alcohol_percentage=alcohol_percentage)
            db.session.add(ingredient)
            db.session.commit()
            return jsonify(ingredient.serialize)
        else:
            return abort(400, "This Ingredient name already exists")
    if request.method == "GET":
        return jsonify([elem.serialize for elem in Ingredient.query.all().order_by()])
        # TODO: allow filtering by alcohol etc.


@app.route("/api/cocktails", methods=["POST", "GET"])
def handle_cocktail():
    if request.method == "POST":
        cocktail_name = request.get_json()["name"]
        ingred_list = request.get_json()["ingredients"]
        # TODO: good checks to make sure the ingred list is ok
        cocktail = Cocktail(name=cocktail_name)
        for ingred_id in ingred_list:
            try:
                ingred = Ingredient.query.filter_by(id=ingred_id).first()
                print(ingred)
                cocktail.ingredients.append(ingred)
            except:
                return abort(400, "Ingredient with ID " + str(ingred_id) +
                             " does not exist")
        db.session.commit()
        return jsonify(cocktail.serialize)

    if request.method == "GET":
        pass

    if __name__ == "__main__":
        app.run(c.DEBUG)
