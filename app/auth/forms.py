# coding: utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('电子邮件:', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('密码:', validators=[DataRequired()])
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    email = StringField('电子邮件:', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('用户名:', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              '用户名只能包含字母、 '
                                              '数字、 . 或 _')])
    password = PasswordField('密码:', validators=[
        DataRequired(), EqualTo('password2', message='两次输入密码不一致！')])
    password2 = PasswordField('确认密码:', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该电子邮件已被注册，请修改密码后登录或使用新的电子邮件.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在.')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')