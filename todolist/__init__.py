from flask import Flask
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from os import path
load_dotenv()
from datetime import timedelta
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
SECRET_KEY = os.environ.get("SECRET_KEY")
DB_NAME = os.environ.get("DB_NAME")

def create_database(app):
     if not path.exists(DB_NAME):
         with app.app_context():
             db.create_all()
         print("Created Database!")

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    # app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Nghiaduong123@127.0.0.1:3306/todolist"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "caotuannghia20000@gmail.com"
app.config["MAIL_PASSWORD"] = "dvtoqoyjocwfbltm"
db.init_app(app)
    
from .model import Note, User
create_database(app)
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)
app.permanent_session_lifetime = timedelta(seconds = 5)
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
mail = Mail(app)
