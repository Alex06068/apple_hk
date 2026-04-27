import os
from dotenv import load_dotenv

# 獲取當前 config.py 所在的資料夾路徑
basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # 修正：將路徑改為當前目錄下的 app.db
    # sqlite:/// (三個斜槓) 表示相對路徑
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False