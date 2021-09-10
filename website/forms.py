from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, DateField
from flask_wtf.file import FileField


class NewForm(FlaskForm):
    title = StringField('title')
    authors = TextAreaField('authors')
    post_url = StringField('post_url')
    summary = TextAreaField('summary')
    abstract = TextAreaField('abstract')
    image_url = StringField('image_url')
    publishdate = DateField('publish')
    journal_ref = StringField('journal_ref')
    doi = StringField('doi')
    tags = StringField('tags')
    unstructured = TextAreaField('unstructured')
    edit_code = StringField('edit_code')
    hidden = BooleanField('hidden')
    image = FileField('image')


class EditForm(FlaskForm):
    title = StringField('title')
    authors = TextAreaField('authors')
    post_url = StringField('post_url')
    summary = TextAreaField('summary')
    abstract = TextAreaField('abstract')
    image_url = StringField('image_url')
    journal_ref = StringField('journal_ref')
    doi = StringField('doi')
    tags = StringField('tags')
    unstructured = TextAreaField('unstructured')
    edit_code = StringField('edit_code')
    autoupdate = BooleanField('autoupdate')
    hidden = BooleanField('hidden')
    image = FileField('image')
