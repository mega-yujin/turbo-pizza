from uuid import UUID
from typing import Union

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import AppSettings, get_settings
from app.pizzeria.models import (
    Pizza,
    PizzaAddedResponse,
    PizzaFoundResponse,
    PizzaDeletedResponse,
    PizzaUpdateRequest,
    PizzaUpdatedResponse
)
from app.system.database import get_db_session
from app.system.schemas import (
    PizzasTable,
    IngredientsTable,
    CategoriesTable,
    pizza_ingredient_table,
)


class PizzeriaService:
    def __init__(
            self,
            db_session: Session = Depends(get_db_session),
            settings: AppSettings = Depends(get_settings),
    ):
        self.db_session = db_session
        self.settings = settings

    def get_pizza(self, name: str) -> PizzaFoundResponse:
        db_pizza = self._get_pizza(name)
        if db_pizza:
            result = PizzaFoundResponse(pizza=Pizza.from_orm(db_pizza))
        else:
            result = PizzaFoundResponse(
                result='fail',
                detail='No such pizza'
            )
        return result

    def _get_pizza(self, name: str) -> Union[PizzasTable, None]:
        return self.db_session.query(PizzasTable).filter(PizzasTable.name == name).first()

    def get_all_pizzas(self) -> list[Pizza]:
        all_pizzas = self.db_session.query(PizzasTable).all()
        return [Pizza.from_orm(pizza) for pizza in all_pizzas]

    def add_pizza(self, pizza: Pizza):
        if self._get_pizza(pizza.name):
            result = PizzaAddedResponse(result='fail', detail='pizza with such name already exists')
        else:
            category = self._get_pizza_category(pizza.category.name)
            ingredients_status = {
                ingredient.name: self._get_ingredient(ingredient.name) for ingredient in pizza.ingredients
            }
            pizza.ingredients = [
                ingredient for ingredient in pizza.ingredients if not ingredients_status.get(ingredient.name)
            ]

            self._insert(
                PizzasTable(
                    id=pizza.id,
                    name=pizza.name,
                    category_id=category.id if category else pizza.category.id,
                    description=pizza.description,
                    price=pizza.price,
                    calories=pizza.calories,
                    weight=pizza.weight,
                    ingredients=[IngredientsTable(**ingredient.dict()) for ingredient in pizza.ingredients],
                    category=CategoriesTable(**pizza.category.dict()) if not category else None
                )
            )
            self._insert_pizza_ingredients(pizza.id, ingredients_status)
            result = PizzaAddedResponse(pizza=pizza)
        return result

    def delete_pizza(self, name: str):
        db_pizza = self.db_session.query(PizzasTable).filter(PizzasTable.name == name).first()
        if db_pizza:
            self.db_session.delete(db_pizza)
            self.db_session.commit()
            result = PizzaDeletedResponse()
        else:
            result = PizzaDeletedResponse(result='Fail', detail='No such pizza')
        return result

    def update_pizza(self, name: str, update_data: PizzaUpdateRequest):
        db_pizza = self.db_session.query(PizzasTable).filter(PizzasTable.name == name)
        if db_pizza:
            db_pizza.update(update_data.dict())
            self.db_session.commit()
            result = PizzaUpdatedResponse(pizza=Pizza.from_orm(db_pizza))
        else:
            result = PizzaUpdatedResponse(result='Fail', detail='No such pizza')
        return result

    def _insert(self, data):
        self.db_session.add(data)
        self.db_session.commit()

    def _insert_many(self, data: list):
        pass

    def _delete(self, data):
        pass

    def _update(self, data):
        pass

    def _insert_pizza_ingredients(self, pizza_id: UUID, ingredients: dict):
        prepared_data = [
            {'pizza_id': pizza_id, 'ingredient_id': ingredient.id}
            for ingredient in ingredients.values() if ingredient
        ]
        self.db_session.execute(pizza_ingredient_table.insert(), prepared_data)
        self.db_session.commit()

    def _get_ingredient(self, ingredient_name: str):
        return self.db_session.query(IngredientsTable).filter(IngredientsTable.name == ingredient_name).first()

    def _get_pizza_category(self, category_name: str):
        return self.db_session.query(CategoriesTable).filter(CategoriesTable.name == category_name).first()
