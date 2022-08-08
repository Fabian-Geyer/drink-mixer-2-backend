from coma2.models.cocktails import Ingredient, Cocktail
from coma2.models.cocktails import db as cocktail_db

cocktail_db.drop_all()
cocktail_db.create_all()

ingred_1 = Ingredient(name="Orangesaft", alcohol_percentage=0)
ingred_2 = Ingredient(name="Wodka", alcohol_percentage=40)
ingred_3 = Ingredient(name="Apfelsaft", alcohol_percentage=0)

cocktail_1 = Cocktail(name="Screwdriver")
cocktail_2 = Cocktail(name="Apfel-O")

cocktail_1.ingredients.append(ingred_1)
cocktail_1.ingredients.append(ingred_2)
cocktail_2.ingredients.append(ingred_1)
cocktail_2.ingredients.append(ingred_3)

cocktail_db.session.add_all([ingred_1, ingred_2, ingred_3])
cocktail_db.session.add_all([cocktail_1, cocktail_2])

cocktail_db.session.commit()