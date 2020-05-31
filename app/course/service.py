import base64
import datetime
import json
import time
import zlib
from typing import Dict

from szpt_course import Course

from app import db
from app.base.api_controller import APIErrorException
from app.common import get_config
from app.course import CourseModel
from app.user import UserService


def data_encode(data):
    data = json.dumps(data).encode('ascii')
    data = zlib.compress(data)
    return base64.b64encode(data).decode('ascii')


def data_decode(data_str: str):
    data = base64.b64decode(data_str.encode('ascii'))
    data = zlib.decompress(data)  # type: bytes
    return json.loads(data.decode('ascii'))


class CourseService:
    class CourseQueryFailedException(APIErrorException):
        code = 2001

    def __init__(self):
        self.course = Course(**get_config('COURSE_CONFIG'))
        self.sync_interval = get_config('COURSE_SYNC_INTERVAL', 3600)

    def query(self, token, sync: bool, week: int=-1, day: int=-1):
        user_info = UserService.get_user_info(token)

        course = CourseModel.query.get(user_info.user_id)  # type: CourseModel
        if course is None:
            course = CourseModel(user_id=user_info.user_id, sync_time=0)

        now = int(time.time())
        if now - course.sync_time >= self.sync_interval or sync:
            info = self.course.query(user_info.number)
            if info is None:
                raise self.CourseQueryFailedException(dict(number=user_info.number))

            items = info['courses']
            user_info.name = info['name']

            courses_items = [item.data for item in items]

            count = {}
            for item in items:
                c = count.get(item.week, 0)
                count[item.week] = c + 1

            course.data = data_encode(courses_items)
            course.count = json.dumps(count)
            course.sync_time = now

            db.session.add(course)
            db.session.add(user_info)
            db.session.commit()
        else:
            courses_items = data_decode(course.data)

        courses = []
        for item in courses_items:
            if (week == -1 or item['week'] == week) and (day == -1 or item['day'] == day):
                courses.append(item)

        return courses

    def info(self, token):
        user_info = UserService.get_user_info(token)

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
                course = CourseModel.query.get(user_info.user_id)  # type: CourseModel
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

        return dict(
            current_info=current_info,
            dates=dates_info,
            weeks=self.course.weeks,
        )
