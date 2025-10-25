from flask import Blueprint, request, jsonify

from coma2.config import db, app
from coma2.slots.models import Slot
from coma2.ingredients.models import Ingredient


slots = Blueprint('slots', __name__)


@slots.route("/api/slots", methods=["PATCH", "GET"])
def handle_slot():
    """Endpoint to get info about slots and to change single slots"""
    if request.method == "PATCH":

        # Unwrap JSON request
        req = request.get_json()

        # Find slot to update
        slot = Slot.query.filter_by(id=req["id"]).first()

        if "ingredient_id" in req.keys():
            # Check if ingredient_id exists
            ingred = Ingredient.query.filter_by(id=req["ingredient_id"]).first()

            # Allow clearing slot by setting ingredient_id to 0
            if req['ingredient_id'] == 0:
                ingred = True  # Allow ingredient_id 0 to clear slot

            # If ingredient does not exist, return error
            if not ingred:
                app.logger.error(f"Ingredient id {req['ingredient_id']} does not exist")
                return jsonify({"error": "Ingredient id does not exist"}), 400

            # Update ingredient in slot
            slot.ingredient_id = req["ingredient_id"]
        
        # Update how much liquid is in the slot if provided
        if "amount_percentage" in req.keys():
            slot.amount_percentage = req["amount_percentage"]

        db.session.commit()
        return jsonify(slot.serialize)
    
    if request.method == "GET":
        return jsonify([elem.serialize for elem in db.session.query(
            Slot).order_by(Slot.id)])
