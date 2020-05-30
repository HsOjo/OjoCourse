from flask import request

from .models import CourseModel
from .service import CourseService
from ..base import APIController


class CourseController(APIController):
    import_name = __name__

    def __init__(self, app):
        super().__init__(app)
        self.service = CourseService()

    def callback_add_routes(self):
        self.add_route('/query', view_func=self.query, methods=['POST'])
        self.add_route('/info', view_func=self.info, methods=['POST'])

    def query(self):
        try:
            data = request.get_json()
            token = data['token']
            sync = data.get('sync', False)
            week = data.get('week')
            day = data.get('day')
        except:
            raise self.ParamsNotMatchException

        courses = self.service.query(token, sync, week, day)
        return self.make_response(courses=courses)

    def info(self):
        try:
            data = request.get_json()
            token = data['token']
        except:
            raise self.ParamsNotMatchException

        info = self.service.info(token)
        return self.make_response(**info)
