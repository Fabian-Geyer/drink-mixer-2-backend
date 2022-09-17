from datetime import datetime

from coma2.settings import db


class CocktailIngredient(db.Model):
    __tablename__ = "cocktail_ingredient"
    cocktail_id = db.Column(db.ForeignKey("cocktail.id"), primary_key=True)
    ingredient_id = db.Column(db.ForeignKey("ingredient.id"), primary_key=True)
    amount = db.Column("amount", db.Integer)
    ingredient = db.relationship("Ingredient", back_populates="cocktails")
    cocktail = db.relationship("Cocktail", back_populates="ingredients")


class Cocktail(db.Model):
    """
    Table to keep track of Cocktails and their names
    """

    __tablename__ = "cocktail"

    id = db.Column("id",
                   db.Integer,
                   primary_key=True,
                   autoincrement=True)
    timestamp = db.Column("timestamp",
                          db.DateTime,
                          nullable=False,
                          default=datetime.utcnow)
    name = db.Column("name",
                     db.String)
    ingredients = db.relationship(
        "CocktailIngredient", back_populates="cocktail")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"""{self.timestamp} {self.id} {self.name}"""

    @property
    def serialize(self):
        """
        Return item in serializeable format
        """
        # Calculate percentage
        total_amount = sum([assoc.amount for assoc in self.ingredients])

        ingredients = []
        for assoc in self.ingredients:
            ingredient = assoc.ingredient.serialize
            ingredient["amount"] = assoc.amount
            ingredient["amount_percentage"] = round(100*assoc.amount/total_amount)
            ingredients.append(ingredient)

        return {"id": self.id,
                "timestamp": self.timestamp,
                "name": self.name,
                "ingredients": ingredients,
                }
