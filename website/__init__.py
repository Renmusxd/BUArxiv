import logging
import os
from website.crud import csrf, crud
from flask import Flask
from website.database import db, init_app
# from flask_cdn import CDN

def fix_dates(date):
    return date.strftime('%Y-%m-%d')

def create_app(config, debug=False, testing=False, config_overrides=None, make_db=False):
    app = Flask(__name__, static_url_path='/cmt-arxiv/static', static_folder='static')
    app.config.from_object(config)
    # CDN(app)

    app.debug = debug
    app.testing = testing

    if config_overrides:
        app.config.update(config_overrides)

    # Configure logging
    if not app.testing:
        logging.basicConfig(level=logging.INFO)
        logging.basicConfig(level=logging.INFO)

    # Setup the data model.
    with app.app_context():
        init_app(app)
        csrf.init_app(app)

        if make_db and not os.path.exists('test.db'):
            db.create_all()

    # Register the Bookshelf CRUD blueprint.
    app.register_blueprint(crud)

    app.jinja_env.globals.update(fix_dates=fix_dates, max=max)

    return app