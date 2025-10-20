from . import db

class Pizza(db.Model):
    __tablename__ = "Pizza"
    pizza_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    price = db.Column(db.Numeric(8, 2), nullable=False)
    is_vegetarian = db.Column(db.Boolean, default=False)
    is_vegan = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    ingredients = db.relationship("PizzaIngredient", back_populates="pizza")
