from flask import Blueprint, request, jsonify

from coma2.config import db, app
from coma2.slots.models import Slot


slots = Blueprint('slots', __name__)


@slots.route("/api/slots", methods=["PATCH", "GET"])
def handle_slot():
    """Endpoint to get info about slots and to change single slots"""
    if request.method == "PATCH":
        req = request.get_json()
        slot = Slot.query.filter_by(id=req["id"]).first()
        if "ingredient_id" in req.keys():
            slot.ingredient_id = req["ingredient_id"]
        if "amount_percentage" in req.keys():
            slot.amount_percentage = req["amount_percentage"]
        db.session.commit()
        return jsonify(slot.serialize)
    if request.method == "GET":
        return jsonify([elem.serialize for elem in db.session.query(
            Slot).order_by(Slot.id)])
