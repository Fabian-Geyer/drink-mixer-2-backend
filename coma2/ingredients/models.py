from datetime import datetime

from coma2.settings import db


class Ingredient(db.Model):
    """
    Table to keep track of all cocktail ingredients
    """

    __tablename__ = "ingredient"

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
    alcohol_percentage = db.Column("alcohol_percentage",
                                   db.Integer)
    cocktails = db.relationship(
        "CocktailIngredient", back_populates="ingredient")

    def __init__(self, name, alcohol_percentage):
        self.name = name
        self.alcohol_percentage = alcohol_percentage

    def __repr__(self):
        return f"""{self.timestamp} {self.id} {self.name} {self.alcohol_percentage}"""

    @property
    def serialize(self):
        """
        Return item in serializeable format
        """
        return {"id": self.id,
                "name": self.name,
                "alcohol_percentage": self.alcohol_percentage
                }
