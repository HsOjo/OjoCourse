import json
import time

from flask import Blueprint, Flask, request, jsonify
from szpt_course import Course

from .models import CourseModel
from .. import db


class CourseController:
    ERR_COMMON_PARAMS_NOT_MATCH = -1
    ERR_QUERY_TOKEN_INVALID = 1000

    blueprint = Blueprint('course', __name__)

    def __init__(self, app: Flask, config: dict):
        self.blueprint.add_url_rule('/query', view_func=self.query, methods=['POST'])
        self.course = Course(**config)

        app.register_blueprint(self.blueprint, url_prefix='/course')

    def query(self):
        try:
            data = request.get_json()
            token = data['token']
            update = data.get('update', False)
        except:
            return jsonify(error=self.ERR_COMMON_PARAMS_NOT_MATCH)

        info = UserInfoModel.query.filter_by(token=token).first()  # type: UserInfoModel
        if info is None:
            return jsonify(error=self.ERR_QUERY_TOKEN_INVALID)

        course = CourseModel.query.get(info.user_id)  # type: CourseModel
        if time.time() - course.update_time > 3600 or update:
            items = self.course.query(info.number)
            data = [i.data for i in items]
            data_str = json.dumps(data)

            course.data = data_str
            course.update_time = time.time()

            db.session.add(course)
            db.session.commit()

        return jsonify(error=0, data=json.loads(course.data))
