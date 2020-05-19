from app import db


class CourseModel(db.Model):
    __tablename__ = 'course'
    user_id = db.Column(db.INTEGER, primary_key=True)
    data = db.Column(db.TEXT)
    update_time = db.Column(db.TIMESTAMP)
