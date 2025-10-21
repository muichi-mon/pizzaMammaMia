from ORM import db
from datetime import datetime

class DeliveryPerson(db.Model):
    __tablename__ = 'DeliveryPerson'
    
    delivery_person_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=False, unique=True)
    postcode = db.Column(db.String(20), nullable=False)
    last_delivery_at = db.Column(db.DateTime, nullable=True)
