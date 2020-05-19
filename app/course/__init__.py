import base64
import json
import time
import traceback
import zlib

from flask import Blueprint, Flask, request, jsonify
from szpt_course import Course

import app.user as U
from .models import CourseModel
from .. import db


def data_encode(data):
    data = json.dumps(data).encode('ascii')
    data = zlib.compress(data)
    return base64.b64encode(data).decode('ascii')


def data_decode(data_str: str):
    data = base64.b64decode(data_str.encode('ascii'))
    data = zlib.decompress(data)  # type: bytes
    return json.loads(data.decode('ascii'))


class CourseController:
    ERR_COMMON_PARAMS_NOT_MATCH = -1
    ERR_QUERY_TOKEN_INVALID = 1000
    ERR_QUERY_QUERY_FAILED = 1001

    blueprint = Blueprint('course', __name__)

    def __init__(self, app: Flask):
        self.blueprint.add_url_rule('/query', view_func=self.query, methods=['POST'])

        config = app.config.get('COURSE_CONFIG')
        self.course = Course(**config)
        self.update_interval = app.config.get('COURSE_UPDATE_INTERVAL')

        app.register_blueprint(self.blueprint, url_prefix='/course')

    def query(self):
        try:
            data = request.get_json()
            token = data['token']
            update = data.get('update', False)
        except:
            return jsonify(error=self.ERR_COMMON_PARAMS_NOT_MATCH, exc=traceback.format_exc())

        info = U.UserInfoModel.query.filter_by(token=token).first()  # type: U.UserInfoModel
        if info is None:
            return jsonify(error=self.ERR_QUERY_TOKEN_INVALID)

        course = CourseModel.query.get(info.user_id)  # type: CourseModel
        if course is None:
            course = CourseModel(user_id=info.user_id, update_time=0)

        now = int(time.time())
        if now - course.update_time >= self.update_interval or update:
            items = self.course.query(info.number)
            if items is None:
                return jsonify(error=self.ERR_QUERY_QUERY_FAILED, number=info.number)

            data = dict(
                info=dict(
                    date=self.course.current_date,
                    stu_year=self.course.current_stu_year,
                    week=self.course.current_week,
                    day=self.course.current_day,
                ),
                courses=[i.data for i in items],
            )

            course.data = data_encode(data)
            course.update_time = now

            db.session.add(course)
            db.session.commit()
        else:
            data = data_decode(course.data)

        return jsonify(error=0, data=data)
