from datetime import date
from sqlalchemy import CheckConstraint
from . import db 

class Customer(db.Model):
    __tablename__ = 'Customer'

    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(254), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    postcode = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)

    __table_args__ = (
        CheckConstraint('birth_date <= CURRENT_DATE', name='chk_birth_date'),
        CheckConstraint("postcode REGEXP '^[0-9]{5}$'", name='chk_postcode'),
    )

    def __repr__(self):
        return f"<Customer {self.first_name} {self.last_name}>"

    def to_dict(self):
        """Optional: Convert object to dictionary (for JSON APIs)"""
        return {
            "customer_id": self.customer_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "birth_date": self.birth_date.isoformat(),
            "postcode": self.postcode
        }
