from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from datetime import date

db = SQLAlchemy()  # Make sure to initialize in your main Flask app

class Customer(db.Model):
    __tablename__ = 'Customer'

    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    postcode = db.Column(db.String(20), nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint('birth_date <= CURRENT_DATE', name='chk_birth_date'),
        CheckConstraint("postcode REGEXP '^[0-9]{5}$'", name='chk_postcode'),
    )

    def __repr__(self):
        return f"<Customer {self.first_name} {self.last_name} (ID: {self.customer_id})>"

    # Optional: serialize for API / JSON
    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "birth_date": self.birth_date.isoformat(),
            "postcode": self.postcode
        }
