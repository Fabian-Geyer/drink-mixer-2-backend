from datetime import datetime

from pydantic import BaseModel, Field


class CocktailIngredientInput(BaseModel):
    ingredient_id: int
    amount: int = Field(gt=0)


class CocktailIngredientRead(BaseModel):
    id: int
    name: str
    alcohol_percentage: int
    amount: int
    amount_percentage: int


class CocktailCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    ingredients: list[CocktailIngredientInput] = Field(min_length=1)


class CocktailUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    ingredients: list[CocktailIngredientInput] | None = Field(default=None, min_length=1)


class CocktailRead(BaseModel):
    id: int
    name: str
    timestamp: datetime
    ingredients: list[CocktailIngredientRead]
