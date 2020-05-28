from flask_login import UserMixin

from app import db


class UserModel(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    username = db.Column(db.VARCHAR(32), unique=True)
    password = db.Column(db.VARCHAR(32))

    info = db.relationship('UserInfoModel', backref='user', uselist=False)  # type: UserInfoModel
    course = db.relationship('CourseModel', backref='user', uselist=False)


class UserInfoModel(db.Model):
    __tablename__ = 'user_info'
    user_id = db.Column(db.INTEGER, db.ForeignKey(UserModel.id), primary_key=True)
    number = db.Column(db.VARCHAR(32))
    name = db.Column(db.VARCHAR(32))
    token = db.Column(db.VARCHAR(64), unique=True)
