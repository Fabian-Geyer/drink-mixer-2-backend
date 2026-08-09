from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from coma2.cocktails.models import Cocktail, CocktailIngredient
from coma2.slots.models import Slot


def get_loaded_ingredient_ids(db: Session) -> set[int]:
    """Ids of every ingredient currently loaded in a non-empty slot."""
    return {
        ingredient_id
        for (ingredient_id,) in db.execute(select(Slot.ingredient_id))
        if ingredient_id != 0
    }


def is_cocktail_available(cocktail: Cocktail, loaded_ingredient_ids: set[int]) -> bool:
    """A cocktail is available when every ingredient it requires is loaded somewhere."""
    return {link.ingredient_id for link in cocktail.ingredients} <= loaded_ingredient_ids


def get_cocktail_with_ingredients(db: Session, cocktail_id: int) -> Cocktail | None:
    return db.get(
        Cocktail,
        cocktail_id,
        options=[selectinload(Cocktail.ingredients).selectinload(CocktailIngredient.ingredient)],
    )
