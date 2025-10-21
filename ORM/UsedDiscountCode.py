from ORM import db
from datetime import datetime

class UsedDiscountCode(db.Model):
    __tablename__ = 'UsedDiscountCode'
    
    customer_id = db.Column(db.Integer, db.ForeignKey('Customer.customer_id'), primary_key=True)
    code = db.Column(db.String(32), db.ForeignKey('DiscountCode.code'), primary_key=True)
    used_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id'), nullable=False)
    
    # Relationships
    customer = db.relationship('Customer', backref='used_discount_codes')
    discount_code = db.relationship('DiscountCode', backref='usage_records')
