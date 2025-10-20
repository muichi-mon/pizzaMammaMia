from . import db
from .Product import Product

class OrderProduct(db.Model):
    __tablename__ = "OrderProduct"
    order_id = db.Column(db.Integer, db.ForeignKey("Order.order_id"), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("Product.product_id"), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    product = db.relationship("Product", back_populates="order_products")
    # order = db.relationship("Order", back_populates="order_products") # if you have Order model
