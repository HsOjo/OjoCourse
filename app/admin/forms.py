from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField(label='用户名', validators=[DataRequired()])
    password = PasswordField(label='密码', validators=[DataRequired()])
    remember = BooleanField(label='记住登录状态')
    submit = SubmitField(label='登录')


class ControlForm(FlaskForm):
    action = SelectField(label='操作', coerce=int, choices=list(
        {
            1: '刷新所有用户课表',
            2: '获取所有用户头像',
        }.items()
    ))
    submit = SubmitField(label='执行')
