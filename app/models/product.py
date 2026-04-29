from app import db

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    subtitle = db.Column(db.String(200))
    description = db.Column(db.Text) 
    image_filename = db.Column(db.String(255)) 
    is_featured = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    # 不要在此處再寫 relationship('Category')，因為 Category 那邊已經寫了 backref