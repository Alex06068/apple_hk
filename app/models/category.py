from app import db

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    # 這裡定義了 backref='category_rel'，代表 Product 對象可以用 .category_rel 訪問分類
    products = db.relationship('Product', backref='category_rel', lazy=True)