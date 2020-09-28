from flask import render_template, flash, redirect, url_for, request

from app import db, common
from app.admin import AdminBaseController
from app.user import UserModel
from .forms import UserEditForm
from ...course import CourseService


class AdminUserController(AdminBaseController):
    import_name = __name__

    def callback_add_routes(self):
        self.add_route('/', self.index)
        self.add_route('/edit/<int:id>', self.edit, methods=['GET', 'POST'])
        self.add_route('/delete/<int:id>', self.delete)
        self.add_route('/sync_course/<int:id>', self.sync_course)

    def index(self):
        pagination = UserModel.query.paginate(None, 20)
        return render_template('admin/user/index.html', pagination=pagination)

    def edit(self, id: int):
        item = UserModel.query.get(id)  # type: UserModel
        if item is None:
            flash('用户不存在', 'danger')

        form = UserEditForm()
        if request.method == 'POST' and form.validate_on_submit():
            item.username = form.username.data
            if form.password.data != '':
                item.password = common.md5(form.password.data)
            item.info.number = form.number.data

            db.session.add(item)
            db.session.commit()

            flash('编辑成功', 'success')
        else:
            form.username.data = item.username
            form.number.data = item.info.number

        return render_template('admin/user/edit.html', form=form)

    def delete(self, id: int):
        item = UserModel.query.get(id)  # type: UserModel
        if item is None:
            flash('用户不存在', 'danger')

        if item.admin:
            db.session.delete(item.admin)
        db.session.delete(item.info)
        if item.course:
            db.session.delete(item.course)
        db.session.commit()
        db.session.delete(item)
        db.session.commit()

        flash('删除成功', 'success')
        return redirect(url_for('admin.user.index'))

    def sync_course(self, id: int):
        item = UserModel.query.get(id)  # type: UserModel
        if item is None:
            flash('用户不存在', 'danger')

        try:
            CourseService().query(item.info.token, True)
            flash('同步成功')
        except Exception as e:
            flash('同步失败 - %a' % e)

        return redirect(url_for('admin.user.index'))
