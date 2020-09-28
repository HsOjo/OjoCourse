import os
import time

from app import db, common
from app.base.api_controller import APIErrorException
from app.common import get_data_path, get_config
from app.user import UserModel, UserInfoModel
from app.utils.edu_admin import EduAdmin


class UserService:
    def __init__(self):
        self.edu_admin = None

        edu_admin_config = get_config('EDU_ADMIN_CONFIG')
        if edu_admin_config is not None:
            self.edu_admin = EduAdmin(**edu_admin_config)

    class UserExistedException(APIErrorException):
        code = 1001
        msg = '注册失败，用户已存在。'

    class UserNotExistedException(APIErrorException):
        code = 1002
        msg = '登录失败，用户名或密码错误。'

    class UserTokenInvalidException(APIErrorException):
        code = 1003
        msg = '用户Token失效，请重新登录账号。'

    def register(self, username, password, number):
        password = common.md5(password)
        if UserModel.query.filter_by(username=username).count() != 0:
            raise self.UserExistedException

        token = self.generate_token(username, number)
        user = UserModel(username=username, password=password, info=UserInfoModel(number=number, token=token))
        db.session.add(user)
        db.session.commit()

        return user.info

    def bind(self, username, password):
        password = common.md5(password)
        user = UserModel.query.filter_by(username=username, password=password).first()  # type: UserModel
        if user is not None:
            user.info.token = self.generate_token(user.username, user.info.number)
            db.session.add(user)
            db.session.commit()
        else:
            raise self.UserNotExistedException

        return user.info

    def get_face(self, number):
        path = os.path.abspath('%s/%s.jpg' % (get_data_path(), number))
        img_data = None

        if not os.path.exists(path):
            if self.edu_admin is not None:
                img_data = self.edu_admin.get_face(number)
            if img_data is not None:
                with open(path, 'wb') as io:
                    io.write(img_data)
        return path

    @staticmethod
    def get_user(username, password):
        password = common.md5(password)
        user = UserModel.query.filter_by(username=username, password=password).first()  # type: UserModel
        return user

    @staticmethod
    def get_user_info(token: str):
        user_info = UserInfoModel.query.filter_by(token=token).first()  # type: UserInfoModel
        if user_info is None:
            raise UserService.UserTokenInvalidException
        return user_info

    @staticmethod
    def generate_token(username, number):
        t = '%s,%s,%d' % (username, number, time.time())
        return common.md5(t)
