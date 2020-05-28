from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user

from .base_controller import AdminBaseController
from .common import get_current_user, admin_required
from .forms import LoginForm, ControlForm
from .models import AdminModel
from .user import AdminUserController
from ..course import CourseService
from ..user import UserService, UserInfoModel


class AdminController(AdminBaseController):
    import_name = __name__

    def __init__(self, app):
        super().__init__(app)
        AdminUserController(app)

    def callback_add_routes(self):
        self.add_route('/login', self.login, methods=['GET', 'POST'], admin_only=False)
        self.add_route('/logout', self.logout)
        self.add_route('/', self.index, methods=['GET', 'POST'])

    def login(self):
        user = get_current_user()
        if not user.is_anonymous and user.admin:
            return redirect(url_for('admin.index'))

        form = LoginForm()
        if request.method == 'POST' and form.validate_on_submit():
            user = UserService.get_user(form.username.data, form.password.data)
            if user is not None and user.admin:
                login_user(user, form.remember.data)
                flash('登录成功', 'success')
                return redirect(url_for('admin.index'))
            flash('登录失败', 'danger')
        return render_template('common/form.html', title='Login', form=form)

    def logout(self):
        logout_user()
        flash('注销成功', 'info')
        return redirect(url_for('admin.login'))

    def index(self):
        form = ControlForm()

        if form.action.data == 1:
            users_info = UserInfoModel.query.all()
            service = CourseService()
            user_info: UserInfoModel
            for user_info in users_info:
                service.query(user_info.token, True)
            flash('刷新完成', 'success')
        elif form.action.data == 2:
            users_info = UserInfoModel.query.all()
            service = UserService()
            user_info: UserInfoModel
            for user_info in users_info:
                service.get_face(user_info.number)
            flash('获取完成', 'success')

        return render_template('admin/form.html', title='后台首页', form=form)
