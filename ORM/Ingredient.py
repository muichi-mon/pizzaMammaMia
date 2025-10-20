from . import db

class Ingredient(db.Model):
    __tablename__ = "Ingredient"

    ingredient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    cost = db.Column(db.Float, nullable=False)
    is_meat = db.Column(db.Boolean, default=False)
    is_animal_prod = db.Column(db.Boolean, default=False)

    # Optional: backref from PizzaIngredient
    pizzas = db.relationship("PizzaIngredient", back_populates="ingredient")
