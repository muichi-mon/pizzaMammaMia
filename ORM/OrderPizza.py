from . import db

class OrderPizza(db.Model):
    __tablename__ = "OrderPizza"
    order_id = db.Column(db.Integer, db.ForeignKey("Orders.order_id"), primary_key=True)
    pizza_id = db.Column(db.Integer, db.ForeignKey("Pizza.pizza_id"), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    name_snapshot = db.Column(db.String(120), nullable=False, default='')

    # Relationships
    order = db.relationship("Order", back_populates="order_pizzas")
    pizza = db.relationship("Pizza")
