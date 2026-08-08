from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from coma2.database import Base
from coma2.ingredients.models import Ingredient


class CocktailIngredient(Base):
    __tablename__ = "cocktail_ingredient"

    cocktail_id: Mapped[int] = mapped_column(ForeignKey("cocktail.id"), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredient.id"), primary_key=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)

    cocktail: Mapped["Cocktail"] = relationship(back_populates="ingredients")
    ingredient: Mapped["Ingredient"] = relationship()


class Cocktail(Base):
    __tablename__ = "cocktail"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    ingredients: Mapped[list[CocktailIngredient]] = relationship(
        back_populates="cocktail", cascade="all, delete-orphan"
    )
