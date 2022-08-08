from coma2.settings import db
from coma2.models.cocktails import db as cocktail_db

cocktail_db.create_all()
