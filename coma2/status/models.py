from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from coma2.database import Base


class Order(Base):
    """A placed (simulated) pour. `order` is reserved in SQL, hence the table name."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cocktail_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cocktail_name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
