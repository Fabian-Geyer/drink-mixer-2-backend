from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from coma2.cocktails.models import Cocktail, CocktailIngredient
from coma2.cocktails.schemas import (
    CocktailCreate,
    CocktailIngredientInput,
    CocktailIngredientRead,
    CocktailRead,
    CocktailUpdate,
)
from coma2.cocktails.service import (
    get_cocktail_with_ingredients,
    get_loaded_ingredient_ids,
    is_cocktail_available,
)
from coma2.database import get_db
from coma2.ingredients.models import Ingredient

router = APIRouter(prefix="/api/cocktails", tags=["cocktails"])


def _to_read_model(cocktail: Cocktail) -> CocktailRead:
    total_amount = sum(link.amount for link in cocktail.ingredients)
    ingredients = [
        CocktailIngredientRead(
            id=link.ingredient.id,
            name=link.ingredient.name,
            alcohol_percentage=link.ingredient.alcohol_percentage,
            amount=link.amount,
            amount_percentage=round(100 * link.amount / total_amount),
        )
        for link in cocktail.ingredients
    ]
    return CocktailRead(
        id=cocktail.id,
        name=cocktail.name,
        timestamp=cocktail.timestamp,
        ingredients=ingredients,
    )


def _get_cocktail_or_404(db: Session, cocktail_id: int) -> Cocktail:
    cocktail = get_cocktail_with_ingredients(db, cocktail_id)
    if cocktail is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cocktail not found")
    return cocktail


def _raise_if_duplicate_name(db: Session, name: str) -> None:
    if db.scalar(select(Cocktail).where(Cocktail.name == name)):
        raise HTTPException(status.HTTP_409_CONFLICT, "A cocktail with this name already exists")


def _build_ingredient_links(
    db: Session, items: list[CocktailIngredientInput]
) -> list[CocktailIngredient]:
    links = []
    for item in items:
        if db.get(Ingredient, item.ingredient_id) is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"Ingredient with id {item.ingredient_id} does not exist",
            )
        links.append(CocktailIngredient(ingredient_id=item.ingredient_id, amount=item.amount))
    return links


@router.post("", response_model=CocktailRead, status_code=status.HTTP_201_CREATED)
def create_cocktail(payload: CocktailCreate, db: Session = Depends(get_db)) -> CocktailRead:
    _raise_if_duplicate_name(db, payload.name)
    cocktail = Cocktail(
        name=payload.name, ingredients=_build_ingredient_links(db, payload.ingredients)
    )
    db.add(cocktail)
    db.commit()
    db.refresh(cocktail)
    return _to_read_model(cocktail)


@router.get("", response_model=list[CocktailRead])
def list_cocktails(db: Session = Depends(get_db)) -> list[CocktailRead]:
    cocktails = db.scalars(
        select(Cocktail)
        .order_by(Cocktail.name)
        .options(selectinload(Cocktail.ingredients).selectinload(CocktailIngredient.ingredient))
    )
    return [_to_read_model(cocktail) for cocktail in cocktails]


@router.get("/available", response_model=list[CocktailRead])
def list_available_cocktails(db: Session = Depends(get_db)) -> list[CocktailRead]:
    """Cocktails whose required ingredients are all currently loaded in some slot."""
    loaded_ingredient_ids = get_loaded_ingredient_ids(db)
    cocktails = db.scalars(
        select(Cocktail).options(
            selectinload(Cocktail.ingredients).selectinload(CocktailIngredient.ingredient)
        )
    )
    available = [
        cocktail for cocktail in cocktails if is_cocktail_available(cocktail, loaded_ingredient_ids)
    ]
    available.sort(key=lambda cocktail: cocktail.name)
    return [_to_read_model(cocktail) for cocktail in available]


@router.get("/{cocktail_id}", response_model=CocktailRead)
def get_cocktail(cocktail_id: int, db: Session = Depends(get_db)) -> CocktailRead:
    return _to_read_model(_get_cocktail_or_404(db, cocktail_id))


@router.put("/{cocktail_id}", response_model=CocktailRead)
def update_cocktail(
    cocktail_id: int, payload: CocktailUpdate, db: Session = Depends(get_db)
) -> CocktailRead:
    cocktail = _get_cocktail_or_404(db, cocktail_id)

    if payload.name is not None and payload.name != cocktail.name:
        _raise_if_duplicate_name(db, payload.name)
        cocktail.name = payload.name

    if payload.ingredients is not None:
        cocktail.ingredients = _build_ingredient_links(db, payload.ingredients)

    db.commit()
    db.refresh(cocktail)
    return _to_read_model(cocktail)


@router.delete("/{cocktail_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cocktail(cocktail_id: int, db: Session = Depends(get_db)) -> None:
    cocktail = _get_cocktail_or_404(db, cocktail_id)
    db.delete(cocktail)
    db.commit()
