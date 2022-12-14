from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import AppSettings, get_settings
from app.orders.models import (
    Order,
    ActiveOrdersResponse,
    OrderAddRequest,
    OrderAddResponse,
    OrderUpdateRequest,
    OrderUpdateResponse,
)
from app.system.database import get_db_session
from app.system.schemas import (
    PizzasTable,
    orders_pizzas_table,
    OrdersTable,
)


class OrdersService:
    def __init__(
            self,
            db_session: Session = Depends(get_db_session),
            settings: AppSettings = Depends(get_settings),
    ):
        self.db_session = db_session
        self.settings = settings

    def get_active_orders(self, user_id: UUID) -> ActiveOrdersResponse:
        db_orders = self.db_session.query(OrdersTable).filter(
            OrdersTable.user_id == user_id
        ).filter(OrdersTable.is_delivered == False).all()  # noqa E712
        if db_orders:
            result = ActiveOrdersResponse(
                orders=[Order.from_orm(order) for order in db_orders]
            )
        else:
            result = ActiveOrdersResponse(detail='No active orders')
        return result

    def get_all_orders(self, user_id: UUID) -> list[Order]:
        db_orders = self.db_session.query(OrdersTable).filter(
            OrdersTable.user_id == user_id
        ).all()
        return [Order.from_orm(order) for order in db_orders]

    def add_order(self, order_in_request: OrderAddRequest, user_id: UUID):
        ordered_pizzas_prices = {
            self.db_session.query(PizzasTable).
            filter(PizzasTable.id == pizza.id).
            first().price: pizza.amount
            for pizza in order_in_request.ordered_items
        }

        total_price = 0
        for price, amount in ordered_pizzas_prices.items():
            total_price += price * amount

        order = Order(
            **order_in_request.dict(), user_id=user_id, total_price=total_price
        )

        self._insert(
            OrdersTable(
                id=order_in_request.id,
                user_id=user_id,
                city=order_in_request.city,
                street=order_in_request.street,
                building=order_in_request.building,
                delivery_time=order_in_request.delivery_time,
                total_price=total_price,
            )
        )
        self._insert_pizzas_to_order(order_in_request)
        result = OrderAddResponse(order=order)
        return result

    def update_order(self, order_id: UUID, update_order: OrderUpdateRequest):
        db_order = self.db_session.query(OrdersTable).filter(OrdersTable.id == order_id)  # noqa: E501
        if db_order:
            db_order.update(
                update_order.dict(exclude_none=True, exclude={'id'})
            )
            self.db_session.commit()
            result = OrderUpdateResponse(
                order=Order.from_orm(db_order.first())
            )
        else:
            result = OrderUpdateResponse(result='Fail', detail='No such order')
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

    def _insert_pizzas_to_order(self, order: OrderAddRequest):
        prepared_data = [
            {'order_id': order.id, 'pizza_id': pizza.id}
            for pizza in order.ordered_items
        ]
        self.db_session.execute(orders_pizzas_table.insert(), prepared_data)
        self.db_session.commit()
