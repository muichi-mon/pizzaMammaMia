from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models so relationships can be resolved
from .Customer import Customer
from .Pizza import Pizza
from .Ingredient import Ingredient
from .PizzaIngredient import PizzaIngredient
