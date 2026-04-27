from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os

# 初始化插件
db = SQLAlchemy()
login_manager = LoginManager()

# 修正：初始化 Admin，移除導致報錯的 template_mode 參數
# 預設即支援 Bootstrap 風格
admin = Admin(name='Apple Store Admin')

def create_app():
    app = Flask(__name__)
    
    # --- 基本配置 ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123456')
    
    # 核心配置：資料庫連線設定
    # 在 GCP/Docker 環境會自動讀取 DATABASE_URL 連接 MySQL，本地則使用 SQLite
    basedir = os.path.abspath(os.path.dirname(__file__))
    default_sqlite = 'sqlite:///' + os.path.join(basedir, 'instance', 'apple_hk.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', default_sqlite)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 圖片上傳配置
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')

    # --- 插件初始化 ---
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # 初始化 Flask-Admin
    admin.init_app(app)

    # --- 匯入模型並加入 Admin 視圖 ---
    # 確保所有資料表（User, Product, Category, Order）都能透過 /admin 管理，符合 20% 分數要求
    from .models.user import User
    from .models.product import Product
    from .models.category import Category
    from .models.order import Order
    
    # 保護機制：避免 Blueprint 命名衝突
    if not admin._views:
        # 使用獨一無二的 endpoint 避免與自定義藍圖衝突
        admin.add_view(ModelView(User, db.session, name="用戶管理", endpoint="admin_user_view"))
        admin.add_view(ModelView(Product, db.session, name="產品管理", endpoint="admin_product_view"))
        admin.add_view(ModelView(Category, db.session, name="類別管理", endpoint="admin_category_view"))
        admin.add_view(ModelView(Order, db.session, name="訂單管理", endpoint="admin_order_view"))

    # --- User Loader ---
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- 註冊藍圖 ---
    # 關鍵修正：匯入已更名的 admin_custom 藍圖
    from .routes import main, admin_bp, auth
    app.register_blueprint(main)
    app.register_blueprint(admin_bp) 
    app.register_blueprint(auth)

    # --- 建立資料庫表 ---
    with app.app_context():
        # 確保本地測試環境的資料夾存在
        if not os.path.exists(os.path.join(basedir, 'instance')):
            os.makedirs(os.path.join(basedir, 'instance'))
        
        # 核心：db.create_all() 會在 Docker 的 MySQL 中自動建立所有表格
        db.create_all()

    return app