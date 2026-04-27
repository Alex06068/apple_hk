from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os

# 初始化插件
db = SQLAlchemy()
login_manager = LoginManager()

# 核心修正：明確指定 url='/admin' 並設定 endpoint，確保 GitHub Codespaces 能正確識別路徑
admin = Admin(name='Apple Store Admin', url='/admin', endpoint='admin')

def create_app():
    app = Flask(__name__)
    
    # --- 基本配置 ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123456')
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    default_sqlite = 'sqlite:///' + os.path.join(basedir, 'instance', 'apple_hk.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', default_sqlite)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')

    # --- 插件初始化 ---
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # 初始化 Flask-Admin
    admin.init_app(app)

    # --- 匯入模型並加入 Admin 視圖 ---
    from .models.user import User
    from .models.product import Product
    from .models.category import Category
    from .models.order import Order
    
    # 保護機制：確保在 Codespaces 重啟時不會重複添加視圖導致報錯
    try:
        admin.add_view(ModelView(User, db.session, name="用戶管理", endpoint="admin_user_view"))
        admin.add_view(ModelView(Product, db.session, name="產品管理", endpoint="admin_product_view"))
        admin.add_view(ModelView(Category, db.session, name="類別管理", endpoint="admin_category_view"))
        admin.add_view(ModelView(Order, db.session, name="訂單管理", endpoint="admin_order_view"))
    except Exception as e:
        print(f"管理視圖註冊提示: {e}")
        
    # --- User Loader ---
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- 註冊藍圖 ---
    # 從 .routes 匯入你剛才修改好的藍圖對象
    from .routes import main, admin_bp, auth
    app.register_blueprint(main)
    app.register_blueprint(admin_bp) 
    app.register_blueprint(auth)

    # --- 建立資料庫表 ---
    with app.app_context():
        if not os.path.exists(os.path.join(basedir, 'instance')):
            os.makedirs(os.path.join(basedir, 'instance'))
        
        # 建立所有資料表以符合 CRUD 功能要求
        db.create_all()

    return app