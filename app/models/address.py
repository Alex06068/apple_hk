from app import db

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address_line = db.Column(db.String(256), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref='addresses')
