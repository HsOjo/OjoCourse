from flask import render_template, flash, redirect, url_for, request

from app import db
from app.admin import AdminBaseController
from app.user import UserModel
from .forms import UserEditForm


class AdminUserController(AdminBaseController):
    import_name = __name__

    def callback_add_routes(self):
        self.add_route('/', self.index)
        self.add_route('/edit/<int:id>', self.edit)
        self.add_route('/delete/<int:id>', self.delete)

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
                item.password = form.password.data
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
        db.session.delete(item.course)
        db.session.commit()
        db.session.delete(item)
        db.session.commit()

        flash('删除成功', 'success')
        return redirect(url_for('admin.user.index'))
