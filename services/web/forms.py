from flask_wtf import FlaskForm
from wtforms import (BooleanField, HiddenField, PasswordField, RadioField, 
                     StringField, SubmitField, TextAreaField)
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня', default=True)
    submit = SubmitField('Отправить')
