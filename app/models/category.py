from app import db

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    # 僅在此處定義關係
    products = db.relationship('Product', backref='category_rel', lazy=True)