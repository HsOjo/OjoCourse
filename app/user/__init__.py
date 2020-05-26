from flask import request, Flask

from .models import UserModel, UserInfoModel
from .sevice import UserService
from ..base import APIController
from ..course import CourseService


class UserController(APIController):
    import_name = __name__

    def __init__(self, app: Flask):
        super().__init__(app)
        self.service = UserService()

        self.service_course = CourseService(
            course_config=app.config.get('COURSE_CONFIG'),
            sync_interval=app.config.get('COURSE_SYNC_INTERVAL'),
        )

    def callback_add_routes(self):
        self.add_route('/register', view_func=self.register, methods=['POST'])
        self.add_route('/bind', view_func=self.bind, methods=['POST'])

    def register(self):
        try:
            data = request.get_json()
            username = data['username']
            password = data['password']
            number = data['number']
        except:
            raise self.ParamsNotMatchException

        user_info = self.service.register(username, password, number)
        self.service_course.query(user_info.token, True, mode=-1)
        user_info = self.service.get_user_info(user_info.token)

        return self.make_response(
            token=user_info.token,
            number=user_info.number,
            name=user_info.name,
        )

    def bind(self):
        try:
            data = request.get_json()
            username = data['username']
            password = data['password']
        except:
            raise self.ParamsNotMatchException

        user_info = self.service.bind(username, password)
        return self.make_response(
            token=user_info.token,
            number=user_info.number,
            name=user_info.name,
        )
