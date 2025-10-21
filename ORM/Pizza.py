from . import db

class Pizza(db.Model):
    __tablename__ = "Pizza"
    pizza_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    active = db.Column(db.Boolean, default=True)

    ingredients = db.relationship("PizzaIngredient", back_populates="pizza")
