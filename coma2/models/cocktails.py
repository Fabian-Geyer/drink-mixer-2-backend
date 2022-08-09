from datetime import datetime

from coma2.settings import db


cocktail_ingredient = db.Table('cocktail_ingredient',
                               db.Column('cocktail_id', db.Integer,
                                         db.ForeignKey('cocktail.id')),
                               db.Column('ingredient_id', db.Integer,
                                         db.ForeignKey('ingredient.id'))
                               )


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
                "timestamp": self.timestamp,
                "name": self.name,
                }


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
        'Ingredient', secondary=cocktail_ingredient, backref='cocktails')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"""{self.timestamp} {self.id} {self.name}"""

    @property
    def serialize(self):
        """
        Return item in serializeable format
        """
        return {"id": self.id,
                "timestamp": self.timestamp,
                "name": self.name,
                "ingredients": [i.name for i in self.ingredients]
                }
