import hashlib
import time

from app import db
from app.base.api_controller import APIErrorException
from app.user import UserModel, UserInfoModel

md5 = lambda x: hashlib.md5(x.encode()).hexdigest()


class UserService:
    class UserExistedException(APIErrorException):
        code = 1001

    class UserNotExistedException(APIErrorException):
        code = 1002

    class UserTokenInvalidException(APIErrorException):
        code = 1003

    def register(self, username, password, number):
        password = md5(password)
        if UserModel.query.filter_by(username=username).count() != 0:
            raise self.UserExistedException

        token = self.generate_token(username, number)
        user = UserModel(username=username, password=password, info=UserInfoModel(number=number, token=token))
        db.session.add(user)
        db.session.commit()

        return user.info

    def bind(self, username, password):
        password = md5(password)
        user = UserModel.query.filter_by(username=username, password=password).first()  # type: UserModel
        if user is not None:
            user.info.token = self.generate_token(user.username, user.info.number)
            db.session.add(user)
            db.session.commit()
        else:
            raise self.UserNotExistedException

        return user.info

    @staticmethod
    def get_user_info(token: str):
        user_info = UserInfoModel.query.filter_by(token=token).first()  # type: UserInfoModel
        if user_info is None:
            raise UserService.UserTokenInvalidException
        return user_info

    @staticmethod
    def generate_token(username, number):
        t = '%s,%s,%d' % (username, number, time.time())
        return md5(t)
