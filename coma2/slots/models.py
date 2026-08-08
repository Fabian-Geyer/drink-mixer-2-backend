from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from coma2.database import Base


class Slot(Base):
    """A physical dispenser port. ingredient_id = 0 means the slot is empty."""

    __tablename__ = "slot"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    amount_percentage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
