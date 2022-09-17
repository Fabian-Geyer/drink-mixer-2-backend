from flask import Blueprint, request, abort, jsonify

from coma2.cocktails.models import Cocktail, CocktailIngredient
from coma2.ingredients.models import Ingredient
from coma2.settings import db

ingredients = Blueprint('ingredients', __name__)

@ingredients.route("/api/ingredients", methods=["POST", "GET", "DELETE"])
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
        return jsonify([elem.serialize for elem in db.session.query(Ingredient).order_by(
            Ingredient.name)])
        # TODO: allow filtering by alcohol etc.
    if request.method == "DELETE":
        id = request.get_json()["id"]
        ingred = Ingredient.query.filter_by(id=id).first()
        if ingred is None:
            abort(400, "This ingredient does not exist")
        # get list of cocktails to delete
        try:
            cocktails_to_delete = [ci.cocktail.id for ci in ingred.cocktails]
            for c_id in cocktails_to_delete:
                Cocktail.query.filter_by(id=c_id).delete()
                CocktailIngredient.query.filter_by(cocktail_id=c_id).delete()
        except:
            pass
        Ingredient.query.filter_by(id=id).delete()
        # TODO: also change slots to id 0 if deleted
        db.session.commit()
        return {}