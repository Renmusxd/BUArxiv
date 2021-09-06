import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class ArxivEntry(db.Model):
    id = db.Column(db.String(80), unique=True, primary_key=True)
    url = db.Column(db.String(256))
    title = db.Column(db.String(256), nullable=False)
    authors = db.Column(db.String(512))
    summary = db.Column(db.String(2048))
    image_url = db.Column(db.String(256))
    timestamp = db.Column(db.TIMESTAMP)

    def __repr__(self):
        return "[{}: {}]".format(self.id, self.title)

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'authors': self.authors,
            'summary': self.summary,
            'image_url': self.image_url,
            'timestamp': self.timestamp
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

    def get_last_n(self, n):
        return ArxivEntry.query.order_by(ArxivEntry.timestamp.desc()).limit(n).all()

    def get_in_previous_days(self, days):
        current_time = datetime.datetime.utcnow()
        days_ago = current_time - datetime.timedelta(days=days)
        return ArxivEntry.query\
            .filter(ArxivEntry.timestamp > days_ago)\
            .order_by(ArxivEntry.timestamp.desc())\
            .all()

    def add_entry(self, id='0', url='localhost', title='Example Title', summary='Example summary',
                  timestamp=None,  image_url=None):
        if timestamp is None:
            timestamp = datetime.date.today()
        entry = ArxivEntry(id=id, title=title, url=url, summary=summary, timestamp=timestamp, image_url=image_url)
        db.session.add(entry)
        db.session.commit()
        return entry

    def edit_by_id(self, id='0', url=None,
                   title=None, summary=None,
                   image_url=None):
        entry = self.get_by_id(id)
        entry.url = url
        entry.title = title
        entry.summary = summary
        entry.image_url = image_url
        db.session.commit()

def get_client():
    return SQLClient.get_client()


def init_app(app):
    # Disable track modifications, as it unnecessarily uses memory.
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    db.init_app(app)
