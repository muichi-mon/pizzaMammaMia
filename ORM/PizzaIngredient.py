from . import db
from .Pizza import Pizza
from .Ingredient import Ingredient

class PizzaIngredient(db.Model):
    __tablename__ = "PizzaIngredient"
    pizza_id = db.Column(db.Integer, db.ForeignKey("Pizza.pizza_id"), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("Ingredient.ingredient_id"), primary_key=True)
    grams = db.Column(db.Integer, nullable=False)

    pizza = db.relationship("Pizza", back_populates="ingredients")
    ingredient = db.relationship("Ingredient")