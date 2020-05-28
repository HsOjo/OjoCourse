from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user

from app import login_manager
from app.user import UserModel


@login_manager.user_loader
def _load_user(id: int):
    admin = UserModel.query.get(id)  # type: UserModel
    return admin


def get_current_user() -> UserModel:
    return current_user


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        user = get_current_user()
        if user.is_anonymous or not user.admin:
            flash('拒绝访问', 'danger')
            return redirect(url_for('admin.login'))
        return func(*args, **kwargs)

    return decorated_view
