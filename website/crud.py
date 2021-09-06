# [START app]
import logging
import sys

import flask
from flask import Flask, Blueprint, send_file, jsonify, render_template, redirect, url_for, abort
from flask_wtf import CSRFProtect

import config
from website.database import get_client
from website.forms import *

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

crud = Blueprint('crud', __name__)

csrf = CSRFProtect()


@crud.route('/')
def index():
    """Return a friendly HTTP greeting."""
    return send_file('static/index.html')


@crud.route('/feed', defaults={'n': 10}, methods=['GET'])
@crud.route('/feed/<n>', methods=['GET'])
def feed(n):
    entries = get_client().get_last_n(n)
    return jsonify([
        entry.to_dict() for entry in entries
    ])


@crud.route('/last/<days>', methods=['GET'])
def last(days):
    entries = get_client().get_in_previous_days(int(days))
    return jsonify([
        entry.to_dict() for entry in entries
    ])


@crud.route('/edit', methods=['GET'])
def listedits():
    entries = get_client().get_last_n(50)
    return render_template('editlist.html', entries=entries)


@crud.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    entry = get_client().get_by_id(id)
    if entry:
        if flask.request.method == 'POST':
            editform = EditForm()
            if editform.validate_on_submit():
                if editform.edit_code.data.strip() == config.EDIT_PASSWORD:
                    get_client().edit_by_id(id,
                                            url=editform.post_url.data.strip(),
                                            title=editform.title.data.strip(),
                                            summary=editform.summary.data.strip(),
                                            image_url=editform.image_url.data.strip())

                    return redirect(url_for('crud.index'))
                else:
                    errors = ["Invalid edit code"]
            else:
               errors = editform.errors.values()
        else:
            errors = []
        print(errors)
        return render_template('edit.html',
                               entry=entry,
                               errors=errors,
                               editform=EditForm())
    else:
        abort(404)


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
