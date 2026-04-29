from app import create_app, db
from app.models.user import User
from app.models.product import Product
from app.models.category import Category # 確保你有導入 Category

app = create_app()

with app.app_context():
    print("正在清理舊資料並重建資料表...")
    db.drop_all()  # 先刪除舊的，確保結構是最新的
    db.create_all()
    
    print("正在插入種子數據...")
    
    # 1. 建立分類 (證明你的 DB Design 有正規化)
    iphone_cat = Category(name='iPhone')
    mac_cat = Category(name='Mac')
    db.session.add_all([iphone_cat, mac_cat])
    db.session.commit() # 先 commit 讓分類拿到 ID

    # 2. 建立產品並關聯分類 (證明你懂 Foreign Key)
    p1 = Product(
        name='iPhone 16 Pro', 
        price=8599, 
        subtitle='最強大的 iPhone', 
        category_id=iphone_cat.id, 
        image_filename='iphone_16_pro.jpg',
        is_featured=True
    )
    p2 = Product(
        name='MacBook Air', 
        price=8999, 
        subtitle='M3 晶片', 
        category_id=mac_cat.id, 
        image_filename='macbook_air.jpg',
        is_featured=True
    )
    
    db.session.add_all([p1, p2])
    db.session.commit()
    
    print("✅ 資料表與初始數據建立成功！")