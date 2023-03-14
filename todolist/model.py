from flask_login import UserMixin
from . import db
from sqlalchemy.sql import func
from .import SECRET_KEY
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class Note(db.Model):
    id=db.Column(db.Integer, primary_key = True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone = True), default = func.now())
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique = True)
    user_name = db.Column(db.String(150))
    password = db.Column(db.String(150))
    notes = db.relationship("Note")
    def __init__(self,email,user_name,password):
        self.email = email
        self.user_name = user_name
        self.password = password

    def get_reset_password_token(self, expires_sec=300):
        serial = Serializer(SECRET_KEY, expires_in=expires_sec)
        return serial.dumps({"user_id":self.id}).decode("utf-8")

    @staticmethod
    def verify_reset_password_token(token):
        serial = Serializer(SECRET_KEY)
        try:
            user_id = serial.loads(token)["user_id"]
        except:
            return None
        
        return User.query.get(user_id)