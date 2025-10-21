from . import db

class DiscountCode(db.Model):
    __tablename__ = "DiscountCode"
    code = db.Column(db.String(32), primary_key=True)
    description = db.Column(db.String(200))
    percent_off = db.Column(db.Numeric(5, 2))
    amount_off = db.Column(db.Numeric(8, 2))
    single_use = db.Column(db.Boolean, default=True)
