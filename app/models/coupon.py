from app import db
from datetime import datetime

class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), unique=True, nullable=False)
    discount_type = db.Column(db.String(20), nullable=False)  # percentage, fixed
    discount_value = db.Column(db.Numeric(10,2), nullable=False)
    min_spend = db.Column(db.Numeric(10,2), default=0)
    expiry_date = db.Column(db.DateTime, nullable=False)
    usage_limit = db.Column(db.Integer, default=1)
    used_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('User', secondary='user_coupon', backref='coupons')

class UserCoupon(db.Model):
    __tablename__ = 'user_coupon'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupon.id'), primary_key=True)
    used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime)
