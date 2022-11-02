import logging

from flask import Flask, render_template, request
from flask_admin import Admin
from flask_login import current_user, LoginManager
from flask_migrate import Migrate

from admin_views import *
from db import db



logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
    level = logging.INFO,
    filename = 'log.log'
    )


app = Flask(__name__)

app.config.from_pyfile('config.py')
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin.login'

admin = Admin(
    template_mode='bootstrap3', 
    name='Админка', 
    index_view=MyHomeView()
    )
admin.init_app(app)
# admin.add_view(UserView(User, db.session))
# admin.add_view(MessageView(Message, db.session))
# admin.add_view(ButtonView(Button, db.session))

admin.add_view(CurrencyPairView(CurrencyPair, db.session, name='Пары'))
admin.add_view(BundleView(Bundle, db.session, name='Связки'))
admin.add_view(AdminView(AdminModel, db.session, name='Админ'))

admin.add_link(LoginMenuLink(name='Логин', category='', url='/admin/login'))
admin.add_link(LogoutMenuLink(name='Выход', category='', url='/admin/logout'))


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    return redirect(url_for('admin.login'))



@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)


@app.route("/media/<path:filename>")
def mediafiles(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["MEDIA_FOLDER"], filename))
    return """
    <!doctype html>
    <title>upload new File</title>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file><input type=submit value=Upload>
    </form>
    """







@login_manager.user_loader
def load_user(user_id):
    return AdminModel.query.get(user_id)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
