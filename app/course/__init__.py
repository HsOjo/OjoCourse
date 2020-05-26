import base64
import datetime
import json
import time
import traceback
import zlib
from typing import Dict

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
    ERR_USER_TOKEN_INVALID = 1000
    ERR_QUERY_QUERY_FAILED = 1001

    QUERY_MODE_ALL = 1
    QUERY_MODE_CURRENT_WEEK = 2
    QUERY_MODE_TODAY = 3

    blueprint = Blueprint('course', __name__)

    def __init__(self, app: Flask):
        self.blueprint.add_url_rule('/query', view_func=self.query, methods=['POST'])
        self.blueprint.add_url_rule('/info', view_func=self.info, methods=['POST'])

        config = app.config.get('COURSE_CONFIG')
        self.course = Course(**config)
        self.course.refresh_state()
        self.sync_interval = app.config.get('COURSE_SYNC_INTERVAL')

        app.register_blueprint(self.blueprint, url_prefix='/course')

    def query(self):
        try:
            data = request.get_json()
            token = data['token']
            sync = data.get('sync', False)
            mode = data.get('mode', self.QUERY_MODE_ALL)
        except:
            return jsonify(error=self.ERR_COMMON_PARAMS_NOT_MATCH, exc=traceback.format_exc())

        info = U.UserInfoModel.query.filter_by(token=token).first()  # type: U.UserInfoModel
        if info is None:
            return jsonify(error=self.ERR_USER_TOKEN_INVALID)

        course = CourseModel.query.get(info.user_id)  # type: CourseModel
        if course is None:
            course = CourseModel(user_id=info.user_id, sync_time=0)

        now = int(time.time())
        if now - course.sync_time >= self.sync_interval or sync:
            items = self.course.query(info.number)
            if items is None:
                return jsonify(error=self.ERR_QUERY_QUERY_FAILED, number=info.number)

            courses = [item.data for item in items]

            count = {}
            for item in items:
                c = count.get(item.week, 0)
                count[item.week] = c + 1

            course.data = data_encode(courses)
            course.count = json.dumps(count)
            course.sync_time = now

            db.session.add(course)
            db.session.commit()
        else:
            courses = data_decode(course.data)

        courses_query = []
        if mode == self.QUERY_MODE_ALL:
            for item in courses:
                courses_query.append(item)
        elif mode == self.QUERY_MODE_CURRENT_WEEK:
            for item in courses:
                if item['week'] == self.course.current_week:
                    courses_query.append(item)
        elif mode == self.QUERY_MODE_TODAY:
            for item in courses:
                if item['week'] == self.course.current_week and item['day'] == self.course.current_day:
                    courses_query.append(item)

        return jsonify(error=0, data=dict(
            courses=courses_query,
        ))

    def info(self):
        try:
            data = request.get_json()
            token = data['token']
        except:
            return jsonify(error=self.ERR_COMMON_PARAMS_NOT_MATCH, exc=traceback.format_exc())

        info = U.UserInfoModel.query.filter_by(token=token).first()  # type: U.UserInfoModel
        if info is None:
            return jsonify(error=self.ERR_USER_TOKEN_INVALID)

        current_info = dict(
            date=self.course.current_date,
            stu_year=self.course.current_stu_year,
            week=self.course.current_week,
            day=self.course.current_day,
        )
        dates = self.course.dates.copy()

        cw, cd = current_info['week'], current_info['day']

        date_c = datetime.datetime.strptime(current_info['date'], '%Y-%m-%d')
        date_d = datetime.datetime.strptime(dates[cw - 1][cd], '%Y-%m-%d')

        if date_c != date_d:
            td_w = (date_d - date_c).days / 7
            if td_w > 0:
                course = CourseModel.query.get(info.user_id)  # type: CourseModel
                if course is not None and course.count is not None:
                    count = json.loads(course.count)  # type: Dict[str, int]
                    for i in range(cw - 1, -1, -1):
                        if count.get('%s' % (i + 1), 0) == 0:
                            dates.insert(i, {})
                            td_w -= 1
                        if td_w == 0:
                            break

        dates_info = {}
        for i, date_w in enumerate(dates, start=1):
            dates_info[i] = date_w

        return jsonify(error=0, data=dict(
            current_info=current_info,
            dates=dates_info,
        ))
