import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql://flaskuser:flaskpass@127.0.0.1/apple_hk'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
