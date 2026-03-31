from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads", "profile_pics")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db = SQLAlchemy(app)

from app import routes, models