from flask_migrate import MigrateCommand
from flask_script import Manager, Shell

from app import app, db
from app.admin import AdminModel
from app.course import CourseModel
from app.user import UserModel, UserInfoModel

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('shell', Shell(
    make_context=lambda: dict(
        CourseModel=CourseModel,
        UserModel=UserModel,
        UserInfoModel=UserInfoModel,
        AdminModel=AdminModel,
        db=db,
    )))


@manager.command
def add_admin():
    username = input('Username:')
    user = UserModel.query.filter_by(username=username).first()  # type: UserModel
    if user is not None:
        admin = AdminModel.query.filter_by(user_id=user.id).first()
        if admin is None:
            admin = AdminModel(user_id=user.id)
            db.session.add(admin)
            db.session.commit()
            print('Admin is added.')
        else:
            print('Admin is existed.')
    else:
        print('User is not exist.')


if __name__ == '__main__':
    manager.run()
