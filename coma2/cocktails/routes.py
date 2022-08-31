from flask import Blueprint, request, abort, jsonify
from coma2.cocktails.models import Cocktail, CocktailIngredient, Ingredient
from coma2.slots.models import Slot
from coma2.settings import db


cocktails = Blueprint('cocktails', __name__)


@cocktails.route("/api/cocktails", methods=["POST", "GET", "DELETE"])
def handle_cocktail():
    if request.method == "POST":
        cocktail_name = request.get_json()["name"]
        # check for duplicates
        duplicate = Cocktail.query.filter_by(name=cocktail_name).first()
        if not duplicate:
            ingred_list = request.get_json()["ingredients"]
            cocktail = Cocktail(name=cocktail_name)
            for i in ingred_list:
                try:
                    ingred = Ingredient.query.filter_by(id=i["id"]).first()
                    cocktail_ingred = CocktailIngredient(amount=i["amount"])
                    cocktail_ingred.ingredient = ingred
                    cocktail.ingredients.append(cocktail_ingred)
                except:
                    return abort(400, "Ingredient with ID " + str(i["i"]) +
                                 " does not exist")
            db.session.commit()
            return jsonify(cocktail.serialize)
        else:
            return abort(400, "Cocktail name already exists")
    if request.method == "GET":
        return jsonify([elem.serialize for elem in db.session.query(
            Cocktail).order_by(Cocktail.name)])
    if request.method == "DELETE":
        id = request.get_json()["id"]
        cocktail = Cocktail.query.filter_by(id=id).first()
        if cocktail is None:
            abort(400, "This cocktail does not exist")
        msg = cocktail.serialize
        Cocktail.query.filter_by(id=id).delete()
        CocktailIngredient.query.filter_by(cocktail_id=id).delete()
        db.session.commit()
        return jsonify(msg)


@cocktails.route("/api/cocktails/available", methods=["GET"])
def handle_available_cocktails():
    if request.method == "GET":
        available_cocktails = []
        for cocktail in db.session.query(Cocktail):
            # get list of needed ingredient ids
            ingreds = []
            for ingred in cocktail.ingredients:
                ingreds.append(ingred.ingredient_id)
            # get list of available ingred ids
            available_ingred_ids = []
            for slot in db.session.query(Slot):
                available_ingred_ids.append(slot.ingredient_id)
            # remove doubles
            available_ingred_ids = [*set(available_ingred_ids)]
            # check if all ids are available
            intersection = list(
                set(ingreds).intersection(available_ingred_ids))
            if (intersection == ingreds):
                available_cocktails.append(cocktail)
        return jsonify([c.serialize for c in available_cocktails])


@cocktails.route("/api/ingredients", methods=["POST", "GET", "DELETE"])
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


# TODO: delete cocktail by id
# TODO: edit cocktail -> delete ingreds by id etc. -> complicated
