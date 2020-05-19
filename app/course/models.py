from app import db
from app.user.models import UserModel


class CourseModel(db.Model):
    __tablename__ = 'course'
    user_id = db.Column(db.INTEGER, db.ForeignKey(UserModel.id), primary_key=True)
    data = db.Column(db.TEXT)
    sync_time = db.Column(db.INTEGER, default=0)
