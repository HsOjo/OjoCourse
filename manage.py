from flask_migrate import MigrateCommand
from flask_script import Manager, Shell

from app import app, db
from app.course import CourseModel
from app.user import UserModel, UserInfoModel

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('shell', Shell(
    make_context=lambda: dict(
        CourseModel=CourseModel,
        UserModel=UserModel,
        UserInfoModel=UserInfoModel,
        db=db,
    )))

if __name__ == '__main__':
    manager.run()
