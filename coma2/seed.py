from sqlalchemy import select
from sqlalchemy.orm import Session

from coma2.cocktails.models import Cocktail, CocktailIngredient
from coma2.database import SessionLocal
from coma2.ingredients.models import Ingredient
from coma2.slots.models import Slot

SLOT_COUNT = 16


def seed(db: Session) -> None:
    """Seed sample data. Safe to call repeatedly - each part only seeds if empty."""
    if db.scalar(select(Ingredient.id).limit(1)) is None:
        _seed_ingredients_and_cocktails(db)
    if db.scalar(select(Slot.id).limit(1)) is None:
        _seed_slots(db)
    db.commit()


def _seed_ingredients_and_cocktails(db: Session) -> None:
    orange = Ingredient(name="Orangesaft", alcohol_percentage=0)
    vodka = Ingredient(name="Wodka", alcohol_percentage=40)
    apple = Ingredient(name="Apfelsaft", alcohol_percentage=0)
    db.add_all([orange, vodka, apple])
    db.flush()  # assigns ids, needed to link CocktailIngredient rows below

    db.add_all(
        [
            Cocktail(
                name="Screwdriver",
                ingredients=[
                    CocktailIngredient(ingredient_id=orange.id, amount=2),
                    CocktailIngredient(ingredient_id=vodka.id, amount=1),
                ],
            ),
            Cocktail(
                name="Apfel-O",
                ingredients=[
                    CocktailIngredient(ingredient_id=orange.id, amount=1),
                    CocktailIngredient(ingredient_id=apple.id, amount=1),
                ],
            ),
        ]
    )


def _seed_slots(db: Session) -> None:
    db.add_all(
        Slot(id=slot_id, ingredient_id=0, amount_percentage=0)
        for slot_id in range(1, SLOT_COUNT + 1)
    )


def main() -> None:
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
