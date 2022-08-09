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
        return jsonify([elem.serialize for elem in db.session.query(Ingredient).order_by(Ingredient.name)])
        # TODO: allow filtering by alcohol etc.


@app.route("/api/cocktails", methods=["POST", "GET"])
def handle_cocktail():
    if request.method == "POST":
        cocktail_name = request.get_json()["name"]
        # check for duplicates
        duplicate = Cocktail.query.filter_by(name=cocktail_name).first()
        if not duplicate:    
            ingred_list = request.get_json()["ingredients"]
            cocktail = Cocktail(name=cocktail_name)
            for ingred_id in ingred_list:
                try:
                    ingred = Ingredient.query.filter_by(id=ingred_id).first()
                    cocktail.ingredients.append(ingred)
                except:
                    return abort(400, "Ingredient with ID " + str(ingred_id) +
                                 " does not exist")
            db.session.commit()
            return jsonify(cocktail.serialize)
        else:
            return abort(400, "Cocktail name already exists")

    if request.method == "GET":
        pass

    if __name__ == "__main__":
        app.run(c.DEBUG)
