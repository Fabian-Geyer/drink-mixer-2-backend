from coma2.models.cocktails import Ingredient, Cocktail, CocktailIngredient
from coma2.models.cocktails import db as cocktail_db

cocktail_db.drop_all()
cocktail_db.create_all()


ingred_1 = Ingredient(name="Orangesaft", alcohol_percentage=0)
ingred_2 = Ingredient(name="Wodka", alcohol_percentage=40)
ingred_3 = Ingredient(name="Apfelsaft", alcohol_percentage=0)

# Cocktail 1
cocktail_1 = Cocktail(name="Screwdriver")
ci_1 = CocktailIngredient(amount=2)
ci_1.ingredient = ingred_1
cocktail_1.ingredients.append(ci_1)
ci_2 = CocktailIngredient(amount=1)
ci_2.ingredient = ingred_2
cocktail_1.ingredients.append(ci_2)


# Cocktail 2
cocktail_2 = Cocktail(name="Apfel-O")
ci_3 = CocktailIngredient(amount=1)
ci_3.ingredient = ingred_1
cocktail_2.ingredients.append(ci_3)
ci_4 = CocktailIngredient(amount=1)
ci_4.ingredient = ingred_3
cocktail_2.ingredients.append(ci_4)

cocktail_db.session.add_all([ingred_1, ingred_2, ingred_3])

cocktail_db.session.commit()
