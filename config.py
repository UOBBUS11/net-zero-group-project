import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'super-secret-key-for-eco-app'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Set via .env file: HERE_API_KEY=your_key_here
    HERE_API_KEY = os.environ.get('HERE_API_KEY', '')