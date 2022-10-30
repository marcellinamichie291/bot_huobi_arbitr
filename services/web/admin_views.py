import os
import sys

from flask import flash, redirect, request, url_for
from flask_admin import AdminIndexView, BaseView, expose
from flask_admin.babel import gettext
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import FileUploadField, ImageUploadField, rules
from flask_admin.helpers import get_redirect_target
from flask_admin.menu import MenuLink
from flask_admin.model.helpers import get_mdict_item_or_list
from flask_login import current_user, login_user, logout_user
from markupsafe import Markup
from wtforms import HiddenField, StringField, TextAreaField
from wtforms.validators import DataRequired, Regexp
from werkzeug.security import generate_password_hash
from sqlalchemy import and_, func, or_

from forms import LoginForm
from models import AdminModel, Bundle, CurrencyPair

from db import db


class MyHomeView(AdminIndexView):

    @expose('/')
    def index(self):
        if current_user.is_authenticated:
            return self.render('admin/index.html')
        else:
            return redirect(url_for('admin.login'))

    @expose('/login')
    def login(self):
        if current_user.is_authenticated:
            return redirect(url_for('admin.index'))

        title = 'Авторизация'
        login_form = LoginForm()
        return self.render('login.html', page_title=title, form=login_form)

    @expose('/process-login', methods=['POST'])
    def process_login(self):
        form = LoginForm()
        if form.validate_on_submit():
            user = AdminModel.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash('Вы вошли на сайт')
                return redirect(url_for('admin.index'))

        flash('Неправильное имя пользователя или пароль')
        return redirect(url_for('admin.login'))

    @expose('/logout')
    def logout(self):
        logout_user()
        flash('Вы успешно разлогинились')
        return redirect(url_for('admin.login'))

    def is_visible(self):
        return False


class UserView(ModelView):
    pass


class MessageView(ModelView):
    can_delete = True
    can_create = True

    form_overrides = dict(text=TextAreaField,
                          markup=TextAreaField)

    form_widget_args = dict(text=dict(rows=8),
                            markup=dict(rows=4))
    form_columns = ('slug', 'text', 'buttons_list', 'markup')
    column_exclude_list = ('image_id', 'image_path')
    column_searchable_list = ('slug', 'text')
    column_default_sort = ('id', True)

    column_labels = dict(text='Текст',
                         buttons_list='Кнопки',
                         markup='Разметка')

    # def on_form_prefill(self, form, id, **kwargs):
    #     form.slug.render_kw = {'readonly': True}

    def is_accessible(self):
        return current_user.is_authenticated


class ButtonView(ModelView):
    can_delete = True
    can_create = True
    column_default_sort = ('id', True)
    # column_exclude_list = ('callback_data',)
    # form_excluded_columns = ('callback_data',)
    column_searchable_list = ('slug',)

    column_labels = dict(message='Сообщение',
                         text='Текст',
                         type_='Тип',
                         callback_data='Колбек данные',
                         inline_url='Инлайн ссылка')

    form_choices = dict(type_=[
        ('inline', 'inline'),
        ('reply', 'reply')
        ])

    def on_form_prefill(self, form, id, **kwargs):
        form.slug.render_kw = {'readonly': True}

    def is_accessible(self):
        return current_user.is_authenticated


class CurrencyPairView(ModelView):
    column_display_pk = True
    column_exclude_list = ('bundle', 'ticker')
    form_excluded_columns = ('ticker', 'reversed_pair', 'huobi_pair', 'bundle_list')
    column_default_sort = ('id')
    
    form_widget_args = dict(ticker=dict(required=False))

    def on_model_change(self, form, model, is_created):
        model.pair = model.pair.upper()
        model.ticker = model.pair.replace('/', '')


class BundleView(ModelView):
    column_display_pk = True
    form_overrides = dict(pairs_order=HiddenField)
    column_list = ('id', 'name', 'sum')

    column_descriptions = dict(
        sum='Сумма в валюте входа и выхода. Например для связки LINK/ETH > LINK/BTC > ETH/BTC будет сумма в ETH')

    @property
    def extra_js(self):
        with self.admin.app.app_context():
            url = url_for('static', filename='js/custom.js')
        return [url]

    def on_model_change(self, form, model, is_created):
        if not model.name:
            model.name = ' > '.join([curr.pair for curr in model.pairs_list])

        if model.pairs_order.endswith(','):
            model.pairs_order = model.pairs_order[:-1]



class AdminView(ModelView):
    can_delete = False
    can_create = False
    can_edit = True
    column_exclude_list = ('password')

    def on_model_change(self, form, model, is_created):
        model.password = generate_password_hash(
            model.password, method='sha256')

    def is_accessible(self):
        return current_user.is_authenticated


class LoginMenuLink(MenuLink):

    def is_accessible(self):
        return not current_user.is_authenticated


class LogoutMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated
