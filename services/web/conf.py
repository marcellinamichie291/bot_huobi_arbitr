import os


SECRET_KEY = 'dfkFFSd112df$$&jfd#@'

SQLALCHEMY_TRACK_MODIFICATIONS = False

DATABASE_URL = os.getenv('DATABASE_URL')
SQLALCHEMY_DATABASE_URI = DATABASE_URL

STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/static"
MEDIA_FOLDER = f"{os.getenv('APP_FOLDER')}/media"

REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
broker = f'redis://default:{REDIS_PASSWORD}@redis:6379/0'

CELERY_CONFIG = {
    'broker_url': broker
}
