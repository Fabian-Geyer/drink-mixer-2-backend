from sqlalchemy import select
from sqlalchemy.orm import Session

from coma2.cocktails.models import Cocktail
from coma2.ingredients.models import Ingredient
from coma2.seed import SLOT_COUNT, seed
from coma2.slots.models import Slot


def test_seed_creates_sample_data(db_session: Session) -> None:
    seed(db_session)

    assert db_session.scalars(select(Ingredient)).all() != []
    assert len(db_session.scalars(select(Cocktail)).all()) == 2
    assert len(db_session.scalars(select(Slot)).all()) == SLOT_COUNT


def test_seed_is_idempotent(db_session: Session) -> None:
    seed(db_session)
    seed(db_session)

    assert len(db_session.scalars(select(Ingredient)).all()) == 3
    assert len(db_session.scalars(select(Cocktail)).all()) == 2
    assert len(db_session.scalars(select(Slot)).all()) == SLOT_COUNT


def test_seed_does_not_reseed_slots_if_already_populated(db_session: Session) -> None:
    db_session.add(Slot(id=1, ingredient_id=0, amount_percentage=0))
    db_session.commit()

    seed(db_session)

    assert len(db_session.scalars(select(Slot)).all()) == 1
