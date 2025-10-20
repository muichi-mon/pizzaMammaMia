from . import db

class Product(db.Model):
    __tablename__ = "Product"
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    category = db.Column(db.String(50))
    cost = db.Column(db.Float, nullable=False)
    active = db.Column(db.Boolean, default=True)

    order_products = db.relationship("OrderProduct", back_populates="product")

    def __repr__(self):
        return f"<Product {self.name} ({self.category}) - ${self.cost}>"
