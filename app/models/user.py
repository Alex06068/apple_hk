from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    # 1. 基礎 ID 欄位
    id = db.Column(db.Integer, primary_key=True)
    
    # 2. 新增：名字與姓氏 (根據設計圖，這兩項是 Yes/Required)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    
    # 3. 帳號資訊 (將 email 長度改為 64 以對齊設計圖)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # 4. 權限與狀態
    active = db.Column(db.Boolean, default=True) 
    is_admin = db.Column(db.Boolean, default=False) 
    
    # 5. 時間戳記 (將名稱改為 created_on 以對齊圖表)
    created_on = db.Column(db.DateTime, default=db.func.current_timestamp())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)