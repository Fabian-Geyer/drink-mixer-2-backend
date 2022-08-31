from coma2.settings import db


class Slot(db.Model):
    """
    Table to keep track of slots and their respective ingredients
    """

    __tablename__ = "slot"

    id = db.Column("id",
                   db.Integer,
                   primary_key=True)
    ingredient_id = db.Column("ingredient_id", db.Integer)
    amount_percentage = db.Column("amount_percentage", db.Integer)

    def __init__(self, id, ingredient_id, amount_percentage):
        self.id = id
        self.ingredient_id = ingredient_id
        self.amount_percentage = amount_percentage

    def __repr__(self):
        return f"""{self.id} {self.ingredient_id} {self.amount_percentage}"""

    @property
    def serialize(self):
        """
        Return item in serializeable format
        """
        return {"id": self.id,
                "ingredient_id": self.ingredient_id,
                "amount_percentage": self.amount_percentage
                }
