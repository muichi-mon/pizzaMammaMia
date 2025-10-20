from . import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = "Order"
    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("Customer.customer_id"), nullable=False)
    order_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False)
    postcode_snapshot = db.Column(db.String(20), nullable=False)
    total_amount = db.Column(db.Float, default=0.0, nullable=False)

    # Relationships
    order_pizzas = db.relationship("OrderPizza", back_populates="order", cascade="all, delete-orphan")
    order_products = db.relationship("OrderProduct", back_populates="order", cascade="all, delete-orphan")
    customer = db.relationship("Customer")
