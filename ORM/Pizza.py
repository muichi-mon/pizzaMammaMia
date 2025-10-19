from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # Make sure to initialize this in your main app

class Pizza(db.Model):
    __tablename__ = 'Pizza'

    pizza_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Pizza {self.name} (ID: {self.pizza_id}, Active: {self.active})>"

    # Optional: helper method to serialize object for JSON/API responses
    def to_dict(self):
        return {
            "pizza_id": self.pizza_id,
            "name": self.name,
            "active": self.active
        }
