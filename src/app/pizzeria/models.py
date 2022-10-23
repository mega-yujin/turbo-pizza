from app.api.models import ORMBaseModel
from typing import Optional
from pydantic import Field, UUID4
from uuid import uuid4


class PizzaCategory(ORMBaseModel):
    id: str = Field(default=str(uuid4()))
    name: str


class Ingredient(ORMBaseModel):
    id: str = Field(default=str(uuid4()))
    name: str


class Pizza(ORMBaseModel):
    id: str = Field(default=str(uuid4()))
    name: str
    category: Optional[PizzaCategory]
    description: Optional[str]
    price: float
    calories: int
    weight: int
    ingredients: list[Ingredient]


class PizzaCreatedResponse(ORMBaseModel):
    result: str
    pizza: Pizza
