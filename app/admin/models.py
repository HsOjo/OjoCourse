from app import db
from app.user import UserModel


class AdminModel(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    user_id = db.Column(db.INTEGER, db.ForeignKey(UserModel.id), unique=True)

    user = db.relationship('UserModel', backref='admin', uselist=False)  # type: UserModel
