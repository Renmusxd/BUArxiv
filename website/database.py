import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ArxivEntry(db.Model):
    id = db.Column(db.String(80), unique=True, primary_key=True)
    url = db.Column(db.String(256))
    title = db.Column(db.String(256))
    authors = db.Column(db.String(512))
    summary = db.Column(db.String(2048))
    abstract = db.Column(db.String(2048))
    image_url = db.Column(db.String(256))
    timestamp = db.Column(db.TIMESTAMP)
    autoupdate = db.Column(db.Boolean)
    tags = db.Column(db.String)
    journal_ref = db.Column(db.String)
    doi = db.Column(db.String)
    unstructured = db.Column(db.String)
    hidden = db.Column(db.Boolean)

    def __repr__(self):
        return "[{}: {}]".format(self.id, self.title)

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'authors': self.authors,
            'summary': self.summary,
            'abstract': self.abstract,
            'image_url': self.image_url,
            'timestamp': self.timestamp,
            'autoupdate': self.autoupdate,
            'journal_ref': self.journal_ref,
            'doi': self.doi,
            'tags': self.tags,
            'unstructured': self.unstructured
        }


class SQLClient(object):
    client = None

    def __init__(self):
        pass

    @staticmethod
    def get_client():
        if SQLClient.client is None:
            SQLClient.client = SQLClient()
        return SQLClient.client

    def get_by_id(self, id):
        arxivsql = ArxivEntry.query.get(id)
        return arxivsql

    def filter_query(self, entries, only_published=False,
                     authors_includes=None, authors_excludes=None,
                     tags_includes=None, tags_excludes=None,
                     journal_includes=None, journal_excludes=None):
        if only_published:
            entries = entries.filter(db.func.coalesce(ArxivEntry.journal_ref, '') != '')
        if authors_includes:
            for authors_include in authors_includes:
                entries = entries.filter(ArxivEntry.authors.contains(authors_include))
        if authors_excludes:
            for authors_exclude in authors_excludes:
                entries = entries.filter(ArxivEntry.authors.contains(authors_exclude).is_(False))
        if tags_includes:
            for tags_include in tags_includes:
                entries = entries.filter(ArxivEntry.tags.contains(tags_include))
        if tags_excludes:
            for tags_exclude in tags_excludes:
                entries = entries.filter(ArxivEntry.tags.contains(tags_exclude).is_(False))
        if journal_includes:
            for journal_include in journal_includes:
                entries = entries.filter(db.func.coalesce(ArxivEntry.journal_ref, '').contains(journal_include))
        if journal_excludes:
            for journal_exclude in journal_excludes:
                entries = entries.filter(db.func.coalesce(ArxivEntry.journal_ref, '').contains(journal_exclude).is_(False))
        return entries

    def get_last(self, end, start=0, **kwargs):
        entries = ArxivEntry.query\
            .filter(ArxivEntry.hidden.is_(False))\
            .order_by(ArxivEntry.timestamp.desc())
        entries = self.filter_query(entries, **kwargs)
        entries = entries.limit(end).all()
        return entries[start:]

    def get_in_previous_days(self, days, **kwargs):
        current_time = datetime.datetime.utcnow()
        days_ago = current_time - datetime.timedelta(days=days)
        entries = ArxivEntry.query\
            .filter(ArxivEntry.timestamp > days_ago)\
            .filter(ArxivEntry.hidden.is_(False))\
            .order_by(ArxivEntry.timestamp.desc())

        entries = self.filter_query(entries, **kwargs)
        return entries.all()

    def add_entry(self, id='0', url='localhost', title='Example Title', abstract='Example abstract',
                  summary='Example summary', journal_ref=None, doi=None, autoupdate=False, timestamp=None,  image_url=None, tags=None,
                  unstructured=None, authors='A. Bee', hidden=False):
        if timestamp is None:
            timestamp = datetime.date.today()
        entry = ArxivEntry(id=id, title=title, url=url, summary=summary,
                           abstract=abstract, timestamp=timestamp,
                           journal_ref=journal_ref, doi=doi,
                           image_url=image_url, autoupdate=autoupdate,
                           tags=tags, unstructured=unstructured,
                           authors=authors, hidden=hidden)
        db.session.add(entry)
        db.session.commit()
        return entry

    def edit_by_id(self, id='0', url=None, title=None, abstract=None,
                   summary=None, autoupdate=False, image_url=None, tags=None,
                   journal_ref=None, doi=None,
                   unstructured=None, authors=None, hidden=False):
        entry = self.get_by_id(id)
        entry.url = url
        entry.title = title
        entry.authors = authors
        entry.abstract = abstract
        entry.summary = summary
        entry.image_url = image_url
        entry.autoupdate = autoupdate
        entry.tags = tags
        entry.unstructured = unstructured
        entry.hidden = hidden
        entry.journal_ref = journal_ref
        entry.doi = doi
        db.session.commit()


def get_client():
    return SQLClient.get_client()


def init_app(app):
    # Disable track modifications, as it unnecessarily uses memory.
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    db.init_app(app)
