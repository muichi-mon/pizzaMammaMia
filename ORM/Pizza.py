from . import db

class Pizza(db.Model):
    __tablename__ = "Pizza"

    pizza_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Pizza {self.name}>"
