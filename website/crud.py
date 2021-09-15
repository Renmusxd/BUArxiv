# [START app]
import logging
import os
import sys
import time

import flask
from flask import Blueprint, send_file, jsonify, render_template, redirect, url_for, abort, send_from_directory
from flask_wtf import CSRFProtect
from werkzeug.utils import secure_filename
import pathlib

import config
from website.database import get_client
from website.forms import *

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

crud = Blueprint('crud', __name__, url_prefix='/cmt-arxiv')

csrf = CSRFProtect()


@crud.route('/')
def index():
    """Return a friendly HTTP greeting."""
    return send_file('static/index.html')

@crud.route('static/<path:path>')
def send_static(path):
    return send_from_directory('static', path=path)


@crud.route('/feed', defaults={'n': 10}, methods=['GET'])
@crud.route('/feed/<int:n>', methods=['GET'])
def feed(n):
    entries = get_client().get_last_n(n)
    response = jsonify([
        entry.to_dict() for entry in entries
    ])
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@crud.route('/last/<int:days>', methods=['GET'])
def last(days):
    entries = get_client().get_in_previous_days(int(days))
    response = jsonify([
        entry.to_dict() for entry in entries
    ])
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@crud.route('/edit', methods=['GET'])
@crud.route('/edit/', methods=['GET'])
def listedits():
    entries = get_client().get_last_n(50)
    return render_template('editlist.html', entries=entries)


@crud.route('/edit/<string:id>', methods=['GET', 'POST'])
def edit(id):
    entry = get_client().get_by_id(id)
    if entry:
        if flask.request.method == 'POST':
            editform = EditForm()
            if editform.validate_on_submit():
                if editform.edit_code.data.strip() == config.EDIT_PASSWORD or not config.EDIT_PASSWORD:
                    if editform.image.data:
                        filename = secure_filename(editform.image.data.filename)
                        filename = id.replace('/', '_') + pathlib.Path(filename).suffix
                        editform.image.data.save(os.path.join(config.SAVE_IMAGE_LOCATION, filename))
                        image_url = config.SAVE_IMAGE_URL_PREFIX + filename
                    else:
                        image_url = editform.image_url.data.strip()

                    get_client().edit_by_id(id,
                                            title=editform.title.data.strip(),
                                            authors=editform.authors.data.strip(),
                                            url=editform.post_url.data.strip(),
                                            summary=editform.summary.data.strip(),
                                            abstract=editform.abstract.data.strip(),
                                            image_url=image_url,
                                            tags=editform.tags.data.strip(),
                                            unstructured=editform.unstructured.data.strip(),
                                            autoupdate=editform.autoupdate.data,
                                            hidden=editform.hidden.data)

                    return redirect(url_for('crud.index'))
                else:
                    errors = ["Invalid edit code"]
            else:
                errors = editform.errors.values()
        else:
            errors = []
        return render_template('edit.html',
                               entry=entry,
                               errors=errors,
                               needs_edit_code=bool(config.EDIT_PASSWORD),
                               editform=EditForm())
    else:
        abort(404)


@crud.route('/new', methods=['GET'])
@crud.route('/new/', methods=['GET'])
def new():
    client = get_client()
    id = hex(hash(time.time()))[2:]
    print("Trying id: {}".format(id))
    while client.get_by_id(id):
        id = hex(hash(time.time()))[2:]
        print("Trying id: {}".format(id))
    return redirect(url_for('crud.new_id', id=str(id)))


@crud.route('/new/<string:id>', methods=['GET', 'POST'])
def new_id(id):
    if get_client().get_by_id(id):
        return "ID Exists: {}".format(flask.escape(id)), 409
    if flask.request.method == 'POST':
        newform = NewForm()
        if newform.validate_on_submit():
            if newform.edit_code.data.strip() == config.EDIT_PASSWORD or not config.EDIT_PASSWORD:
                print(newform.publishdate.data)
                get_client().add_entry(id,
                                       title=newform.title.data.strip(),
                                       authors=newform.authors.data.strip(),
                                       url=newform.post_url.data.strip(),
                                       summary=newform.summary.data.strip(),
                                       timestamp=newform.publishdate.data,
                                       abstract=newform.abstract.data.strip(),
                                       image_url=newform.image_url.data.strip(),
                                       tags=newform.tags.data.strip(),
                                       unstructured=newform.unstructured.data.strip(),
                                       autoupdate=False,
                                       hidden=newform.hidden.data)

                return redirect(url_for('crud.index'))
            else:
                errors = ["Invalid edit code"]
        else:
           errors = newform.errors.values()
    else:
        errors = []
    return render_template('new.html',
                           id=id,
                           errors=errors,
                           needs_edit_code=bool(config.EDIT_PASSWORD),
                           newform=NewForm())


@crud.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


@crud.errorhandler(404)
def server_error(e):
    return """
    Page was not found: <pre>{}</pre>
    """.format(e), 404
