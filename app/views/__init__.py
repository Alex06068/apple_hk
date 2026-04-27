# 從各自的文件中導入我們定義好的藍圖對象
from .main import main_bp
from .auth import auth as auth_bp
# 如果你有 admin.py，請確保裡面定義的是 admin_bp = Blueprint('admin', ...)
try:
    from .admin import admin_bp
except ImportError:
    admin_bp = None