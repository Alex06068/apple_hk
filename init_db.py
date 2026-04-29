from app import create_app, db
from app.models.product import Product
from app.models.category import Category

app = create_app()

with app.app_context():
    print("正在清理舊資料並重建資料表...")
    db.drop_all()
    db.create_all()

    print("正在插入豐富的種子數據...")

    # 1. 建立分類 (移除報錯的 icon 參數)
    cat_iphone = Category(name='iPhone')
    cat_mac = Category(name='Mac')
    cat_ipad = Category(name='iPad')
    db.session.add_all([cat_iphone, cat_mac, cat_ipad])
    db.session.commit()

    # 2. 建立多樣化產品
    products = [
        # iPhone 系列
        Product(
            name='iPhone 16 Pro', 
            price=8599, 
            subtitle='鈦金屬設計，強大的 A18 Pro 晶片', 
            description='• 6.3 吋顯示器\n• 4800 萬像素主鏡頭\n• 5 倍光學變焦',
            category_id=cat_iphone.id, 
            image_filename='iphone_16_pro.jpg',
            is_featured=True
        ),
        Product(
            name='iPhone 16', 
            price=6899, 
            subtitle='多彩設計，全新的相機控制', 
            description='• 6.1 吋顯示器\n• A18 晶片\n• 超廣角相機升級',
            category_id=cat_iphone.id, 
            image_filename='iphone_16.jpg',
            is_featured=True
        ),
        # Mac 系列
        Product(
            name='MacBook Air 13', 
            price=8999, 
            subtitle='超纖薄，超快速，由 M3 驅動', 
            description='• 13.6 吋 Liquid Retina 顯示器\n• 18 小時電池續航力\n• 無風扇靜音設計',
            category_id=cat_mac.id, 
            image_filename='macbook_air.jpg',
            is_featured=True
        ),
        Product(
            name='MacBook Pro 14', 
            price=12999, 
            subtitle='為專業人士而造的強大動力', 
            description='• M3 Pro 或 M3 Max 晶片\n• Extreme Dynamic Range 顯示器\n• 專業級連接埠',
            category_id=cat_mac.id, 
            image_filename='macbook_pro.jpg',
            is_featured=True
        ),
        # iPad 系列
        Product(
            name='iPad Pro', 
            price=7999, 
            subtitle='超乎想像的薄，強到橫空出世', 
            description='• Ultra Retina XDR 顯示器\n• M4 晶片性能極限\n• 支援 Apple Pencil Pro',
            category_id=cat_ipad.id, 
            image_filename='ipad_pro.jpg',
            is_featured=True
        )
    ]

    db.session.add_all(products)
    db.session.commit()
    print("✅ 成功插入 5 個精選產品！")