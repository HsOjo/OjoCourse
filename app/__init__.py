from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


class Application(Flask):
    def __init__(self):
        super().__init__(__name__)
        self.config.from_pyfile('../config.py')
        db.init_app(self)
        self.register_controllers()

    def register_controllers(self):
        from .user import UserController
        UserController(self)

        from .course import CourseController
        CourseController(self)


db = SQLAlchemy()
app = Application()
migrate = Migrate(app, db)
