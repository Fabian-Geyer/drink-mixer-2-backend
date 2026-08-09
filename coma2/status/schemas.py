from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from coma2.slots.schemas import SlotRead


class OrderCreate(BaseModel):
    cocktail_id: int


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cocktail_id: int
    cocktail_name: str
    created_at: datetime
    duration_seconds: int


class MachineStatus(BaseModel):
    state: Literal["idle", "mixing"]
    current_order: OrderRead | None
    seconds_remaining: float | None
    slots: list[SlotRead]
