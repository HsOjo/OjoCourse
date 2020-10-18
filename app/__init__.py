import os

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from . import common, filter


class Application(Flask):
    def __init__(self):
        super().__init__(__name__)

        program_path = os.path.join(self.root_path, '..')
        self.config.from_pyfile(os.path.join(program_path, 'config.py'))
        os.makedirs(os.path.join(program_path, 'data'), exist_ok=True)

        common.current_app = self
        db.init_app(self)
        login_manager.init_app(self)
        bootstrap.init_app(self)
        bootstrap_cdns = self.extensions['bootstrap']['cdns']
        bootstrap_cdns['bootstrap'] = bootstrap_cdns['local']
        bootstrap_cdns['jquery'] = bootstrap_cdns['local']

        common.register_all_callable_object_from_package(filter, True)
        self.register_controllers()

    def register_controllers(self):
        from .user import UserController
        UserController(self)

        from .course import CourseController
        CourseController(self)

        from .admin import AdminController
        AdminController(self)


db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap()
app = Application()
migrate = Migrate(app, db)
