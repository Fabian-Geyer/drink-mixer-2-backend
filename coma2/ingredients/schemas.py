from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class IngredientBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    alcohol_percentage: int = Field(ge=0, le=100)


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    alcohol_percentage: int | None = Field(default=None, ge=0, le=100)


class IngredientRead(IngredientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
