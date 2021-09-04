# [START app]
import logging
import sys

from flask import Flask, Blueprint, send_file, jsonify
from flask_wtf import CSRFProtect
from website.database import get_client

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
