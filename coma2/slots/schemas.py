from pydantic import BaseModel, ConfigDict, Field


class SlotUpdate(BaseModel):
    ingredient_id: int | None = Field(default=None, ge=0)
    amount_percentage: int | None = Field(default=None, ge=0, le=100)


class SlotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ingredient_id: int
    amount_percentage: int
