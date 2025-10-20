from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models here so relationships can resolve
from .Customer import Customer
from .Pizza import Pizza
from .PizzaIngredient import PizzaIngredient
from .Ingredient import Ingredient
from .Product import Product
from .OrderProduct import OrderProduct
from .Order import Order
from .OrderPizza import OrderPizza