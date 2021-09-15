import os

EDIT_PASSWORD = os.environ['FLASK_EDIT_PASSWORD'] if 'FLASK_EDIT_PASSWORD' in os.environ else ''
SECRET_KEY = os.environ['FLASK_SECRET_KEY'] if 'FLASK_SECRET_KEY' in os.environ else 'secret'
WTF_CSRF_TIME_LIMIT = 7200

SQLALCHEMY_DATABASE_URI = 'sqlite:///../test.db'

MAX_CONTENT_LENGTH = 8 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
SAVE_IMAGE_LOCATION = 'website/static/img/'
SAVE_IMAGE_URL_PREFIX = 'static/img/'
