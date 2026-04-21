from app import db
from datetime import datetime

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    method = db.Column(db.String(32), nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    status = db.Column(db.String(20), default='pending')
    paid_at = db.Column(db.DateTime)
    order = db.relationship('Order', backref='payment')
