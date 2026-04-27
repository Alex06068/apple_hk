from app import create_app, db
# 這裡導入 Model 是為了讓 SQLAlchemy 知道要建立哪些表
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem

app = create_app()
with app.app_context():
    print("正在清理舊資料並重建資料表...")
    db.create_all()
    print("✅ 資料表建立成功！現在你可以執行 python run.py 了。")