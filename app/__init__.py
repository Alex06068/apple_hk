from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    login.login_view = 'auth.login'
    login.login_message = '請先登入'

    @login.user_loader
    def load_user(user_id):
        from .models.user import User
        return User.query.get(int(user_id))

    # 导入所有模型（确保 SQLAlchemy 检测到）
    from .models import user, product, category, review, cart, address, payment, order, coupon, wishlist, notification

    # 注册蓝图
    from .views.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .views.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .views.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    # 自动创建所有表（如果不存在）
    with app.app_context():
        db.create_all()

    return app