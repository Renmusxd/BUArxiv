import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists
from sqlalchemy.orm import Session
from website.database import ArxivEntry
import logging
from PIL import Image
import os

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)


def none_if_empty(s):
    if s:
        return s
    else:
        return None

def run(db_file, tag_prefix='arxiv:'):
    engine = create_engine(db_file, echo=False, future=True)
    if not database_exists(engine.url):
        return

    with Session(engine) as session:
        all = session.query(ArxivEntry).all()
        for entry in all:
            if entry.tags:
                tags = sorted((tag_prefix + tag.strip() if ':' not in tag else tag.strip()) for tag in entry.tags.split(',') if tag.strip())
                entry.tags = ", ".join(tags) + ','

            entry.url = none_if_empty(entry.url)
            entry.title = none_if_empty(entry.title)
            entry.authors = none_if_empty(entry.authors)
            entry.abstract = none_if_empty(entry.abstract)
            entry.summary = none_if_empty(entry.summary)
            entry.image_url = none_if_empty(entry.image_url)
            entry.tags = none_if_empty(entry.tags)
            entry.unstructured = none_if_empty(entry.unstructured)
            entry.journal_ref = none_if_empty(entry.journal_ref)
            entry.doi = none_if_empty(entry.doi)

            session.commit()

if __name__ == "__main__":
    run('sqlite:///test.db')