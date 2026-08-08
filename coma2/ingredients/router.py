from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from coma2.database import get_db
from coma2.ingredients.models import Ingredient
from coma2.ingredients.schemas import IngredientCreate, IngredientRead, IngredientUpdate

router = APIRouter(prefix="/api/ingredients", tags=["ingredients"])


def _get_ingredient_or_404(db: Session, ingredient_id: int) -> Ingredient:
    ingredient = db.get(Ingredient, ingredient_id)
    if ingredient is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ingredient not found")
    return ingredient


def _raise_if_duplicate_name(db: Session, name: str) -> None:
    if db.scalar(select(Ingredient).where(Ingredient.name == name)):
        raise HTTPException(status.HTTP_409_CONFLICT, "An ingredient with this name already exists")


@router.post("", response_model=IngredientRead, status_code=status.HTTP_201_CREATED)
def create_ingredient(payload: IngredientCreate, db: Session = Depends(get_db)) -> Ingredient:
    _raise_if_duplicate_name(db, payload.name)
    ingredient = Ingredient(**payload.model_dump())
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


@router.get("", response_model=list[IngredientRead])
def list_ingredients(db: Session = Depends(get_db)) -> list[Ingredient]:
    return list(db.scalars(select(Ingredient).order_by(Ingredient.name)))


@router.get("/{ingredient_id}", response_model=IngredientRead)
def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)) -> Ingredient:
    return _get_ingredient_or_404(db, ingredient_id)


@router.put("/{ingredient_id}", response_model=IngredientRead)
def update_ingredient(
    ingredient_id: int, payload: IngredientUpdate, db: Session = Depends(get_db)
) -> Ingredient:
    ingredient = _get_ingredient_or_404(db, ingredient_id)

    updates = payload.model_dump(exclude_unset=True)
    if "name" in updates and updates["name"] != ingredient.name:
        _raise_if_duplicate_name(db, updates["name"])

    for field, value in updates.items():
        setattr(ingredient, field, value)

    db.commit()
    db.refresh(ingredient)
    return ingredient


@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)) -> None:
    ingredient = _get_ingredient_or_404(db, ingredient_id)
    db.delete(ingredient)
    db.commit()
