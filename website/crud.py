# [START app]
import logging
import os
import sys
import time

import flask
from flask import Blueprint, send_file, jsonify, render_template, redirect, url_for, abort, send_from_directory, request
from flask_wtf import CSRFProtect
from werkzeug.utils import secure_filename
import pathlib
from PIL import Image

import config
from website.database import get_client
from website.forms import *

crud = Blueprint('crud', __name__, url_prefix='/cmt-arxiv')

csrf = CSRFProtect()


@crud.route('/')
def index():
    """Return a friendly HTTP greeting."""
    return send_file('static/index.html')


@crud.route('/how-do-I-edit')
def edit_instructions():
    """Return a friendly HTTP greeting."""
    return send_file('static/instructions.html')

@crud.route('static/<path:path>')
def send_static(path):
    return send_from_directory('static', path=path)

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def parse_possible_range(numstr):
    if is_int(numstr):
        n = 0
        m = int(numstr)
        return n, m
    else:
        n, m = numstr.split('-')
        if is_int(n) and is_int(m):
            n = int(n)
            m = int(m)
            return n, m
    return None

def parse_filters():
    # Get filters
    only_published = request.args.get('only_published', '')
    if not only_published or only_published == 'false' or only_published == 'False':
        only_published = False
    elif only_published:
        only_published = True

    authors_includes = request.args.getlist('authors_includes')
    authors_excludes = request.args.getlist('authors_excludes')
    tags_includes = request.args.getlist('tags_includes')
    tags_excludes = request.args.getlist('tags_excludes')
    journal_includes = request.args.getlist('journal_includes')
    journal_excludes = request.args.getlist('journal_excludes')

    return {
        'only_published': only_published,
        'authors_includes': authors_includes,
        'authors_excludes': authors_excludes,
        'tags_includes': tags_includes,
        'tags_excludes': tags_excludes,
        'journal_includes': journal_includes,
        'journal_excludes': journal_excludes,
    }

@crud.route('/feed', defaults={'num': '10'}, methods=['GET'])
@crud.route('/feed/', defaults={'num': '10'}, methods=['GET'])
@crud.route('/feed/<string:num>',  methods=['GET'])
def feed(num):
    res = parse_possible_range(num)
    if res is None:
        return "Not found", 404
    else:
        n, m = res
    filters = parse_filters()
    entries = get_client().get_last(m, start=n, **filters)
    response = jsonify([
        entry.to_dict() for entry in entries
    ])
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@crud.route('/last', defaults={'days': 30}, methods=['GET'])
@crud.route('/last/', defaults={'days': 30},  methods=['GET'])
@crud.route('/last/<int:days>', methods=['GET'])
def last(days):
    filters = parse_filters()
    entries = get_client().get_in_previous_days(days, **filters)
    response = jsonify([
        entry.to_dict() for entry in entries
    ])
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@crud.route('/edit', methods=['GET'])
@crud.route('/edit/', methods=['GET'])
def listedits():
    end = request.args.get('end', '50')
    if is_int(end):
        end = int(end)
    else:
        end = 50
    start = request.args.get('start', '0')
    if is_int(start):
        start = int(start)
    else:
        start = 0

    filters = parse_filters()
    entries = get_client().get_last(end, start=start, **filters)
    return render_template('editlist.html', entries=entries, start=start, end=end, perpage=50, filters=filters)


@crud.route('/edit/<path:id>', methods=['GET', 'POST'])
def edit(id):
    entry = get_client().get_by_id(id)
    if entry:
        if flask.request.method == 'POST':
            editform = EditForm()
            if editform.validate_on_submit():
                if editform.edit_code.data.strip() == config.EDIT_PASSWORD or not config.EDIT_PASSWORD:
                    if editform.image.data:
                        # Save full sized
                        filename = secure_filename(editform.image.data.filename)
                        filename = id.replace('/', '_') + pathlib.Path(filename).suffix
                        image_path = os.path.join(config.SAVE_IMAGE_LOCATION, filename)
                        editform.image.data.save(image_path)
                        image_url = config.SAVE_IMAGE_URL_PREFIX + filename
                        # Now make thumbnail
                        try:
                            im = Image.open(request.files[editform.image.name])
                            im.thumbnail(config.THUMBNAIL_SIZE, Image.ANTIALIAS)
                            thumbnail_path = os.path.join(config.SAVE_IMAGE_THUMBNAIL_LOCATION, filename)
                            im.save(thumbnail_path, "png")
                            image_url = config.SAVE_IMAGE_THUMBNAIL_URL_PREFIX + filename
                        except IOError:
                            print("cannot create thumbnail for {}".format(editform.image.name))

                    else:
                        image_url = editform.image_url.data.strip()

                    get_client().edit_by_id(id,
                                            title=editform.title.data.strip(),
                                            authors=editform.authors.data.strip(),
                                            url=editform.post_url.data.strip(),
                                            journal_ref=editform.journal_ref.data.strip(),
                                            doi=editform.doi.data.strip(),
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
                if newform.image.data:
                    # Save full sized
                    filename = secure_filename(newform.image.data.filename)
                    filename = id.replace('/', '_') + pathlib.Path(filename).suffix
                    image_path = os.path.join(config.SAVE_IMAGE_LOCATION, filename)
                    newform.image.data.save(image_path)
                    image_url = config.SAVE_IMAGE_URL_PREFIX + filename
                    # Now make thumbnail
                    try:
                        im = Image.open(request.files[newform.image.name])
                        im.thumbnail(config.THUMBNAIL_SIZE, Image.ANTIALIAS)
                        thumbnail_path = os.path.join(config.SAVE_IMAGE_THUMBNAIL_LOCATION, filename)
                        im.save(thumbnail_path, "png")
                        image_url = config.SAVE_IMAGE_THUMBNAIL_URL_PREFIX + filename
                    except IOError:
                        print("cannot create thumbnail for {}".format(newform.image.name))
                else:
                    image_url = newform.image_url.data.strip()

                get_client().add_entry(id,
                                       title=newform.title.data.strip(),
                                       authors=newform.authors.data.strip(),
                                       journal_ref=newform.journal_ref.data.strip(),
                                       doi=newform.doi.data.strip(),
                                       url=newform.post_url.data.strip(),
                                       summary=newform.summary.data.strip(),
                                       timestamp=newform.publishdate.data,
                                       abstract=newform.abstract.data.strip(),
                                       image_url=image_url,
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
