from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired


class UploadForm(FlaskForm):
    title = StringField('title')
    description = FileField('description')
    body = FileField('body')
    thumbnail = FileField('thumbnail')
    resources = FileField('resources')
    post = SelectField('post')


class EditForm(FlaskForm):
    title = StringField('title')
    authors = TextAreaField('authors')
    post_url = StringField('post_url')
    summary = TextAreaField('summary')
    image_url = StringField('image_url')
    edit_code = StringField('edit_code')
    # thumbnail = FileField('thumbnail')
    # resources = FileField('resources')
    # post = SelectField('post')
