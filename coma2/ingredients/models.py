from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from coma2.database import Base


class Ingredient(Base):
    __tablename__ = "ingredient"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    alcohol_percentage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
