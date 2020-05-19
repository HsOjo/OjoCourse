import hashlib
import time

from flask import Blueprint, request, Flask, jsonify

from app import db
from .models import UserModel, UserInfoModel


def generate_token(username, number):
    t = '%s,%s,%d' % (username, number, time.time())
    h = hashlib.md5(t.encode()).hexdigest()
    return h


class UserController:
    ERR_COMMON_PARAMS_NOT_MATCH = -1
    ERR_REGISTER_EXISTED = 1000
    ERR_BIND_USER_NOT_EXISTED = 2000

    blueprint = Blueprint('user', __name__)

    def __init__(self, app: Flask):
        self.blueprint.add_url_rule('/register', view_func=self.register, methods=['POST'])
        self.blueprint.add_url_rule('/bind', view_func=self.bind, methods=['POST'])

        app.register_blueprint(self.blueprint, url_prefix='/user')

    def register(self):
        try:
            data = request.get_json()
            username = data['username']
            number = data['number']
            password = data['password']
        except:
            return jsonify(error=self.ERR_COMMON_PARAMS_NOT_MATCH)

        if UserModel.query.filter_by(username=username).count() != 0:
            return jsonify(error=self.ERR_REGISTER_EXISTED)
        else:
            token = generate_token(username, number)
            user = UserModel(username=username, password=password, info=UserInfoModel(number=number, token=token))
            db.session.add(user)
            db.session.commit()
            return jsonify(error=0, token=user.info.token)

    def bind(self):
        try:
            data = request.get_json()
            username = data['username']
            password = data['password']
        except:
            return jsonify(error=self.ERR_COMMON_PARAMS_NOT_MATCH)

        user = UserModel.query.filter_by(username=username, password=password).first()  # type: UserModel
        if user is not None:
            user.info.token = generate_token(user.username, user.info.number)
            db.session.add(user)
            db.session.commit()
            return jsonify(error=0, token=user.info.token)
        else:
            return jsonify(error=self.ERR_BIND_USER_NOT_EXISTED)
