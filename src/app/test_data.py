from app.system.database import SessionLocal
from app.auth.models import User
from app.pizzeria.models import Pizza, PizzaCategory, Ingredient
from app.system.database import engine
from src.app.system.database import Base
from app.system.db_tables import (
    pizza_ingredient_table,
    IngredientsTable,
    PizzasTable,
    UsersTable
)


### TESTDATA ###


def create_user(db: SessionLocal, user: User):
    password = 'ololo'
    db_user = UsersTable(
        id=user.id,
        username=user.username,
        email=user.email,
        hashed_password=password,
        is_active=user.is_active,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def add_ingredients(db: SessionLocal, category: PizzaCategory):
    db_category = IngredientsTable(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


USERS = [
    User(
        id='857cbf13-d22a-4d1c-91ff-b74de2d916d8',
        username='finik',
        email='kot@mail.com',
        is_active=True,
    ),
    User(
        id='317cbf13-d22a-4d1c-91ff-b74de2d916d8',
        username='papa',
        email='papa@mail.com',
        is_active=True,
    )
]

INGREDIENTS = [
    Ingredient(
        id='857cbf13-d22a-4d1c-91ff-b74de2d916d2',
        name='cheese',
    ),
    Ingredient(
        id='561cbf13-d22a-4d1c-91ff-b74de2d916d2',
        name='tomato',
    ),
    Ingredient(
        id='857cbf13-4fg2-4d1c-91ff-b74de2d916d2',
        name='mozarella',
    )
]

PIZZAS = [
    Pizza(
        id='857cbf13-4fg2-4d1c-91ff-b74de2d9112g',
        name='margherita',
        category='classic',
        description='mega pizza',
        price=20.5,
        calories=520,
        weight=320,
        ingredients=(
            Ingredient(
                id='857cbf13-4fg2-4d1c-91ff-b74de2d916d2',
                name='mozarella',
            ),
            Ingredient(
                id='561cbf13-d22a-4d1c-91ff-b74de2d916d2',
                name='tomato',
            ),
        ),
    )
]

### TABLES CREATION ###

# tables = [PizzasTable.__table__, IngredientsTable.__table__, ]
# Base.metadata.create_all(engine, tables=tables)
#
# pizza_ingredient_table.create(engine)

### INSERT DATA INTO DATABASE ###

db_session = SessionLocal()

for user in USERS:
    create_user(db_session, user)

# for ing in INGREDIENTS:
#     add_ingredients(db_session, ing)