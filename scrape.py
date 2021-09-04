import arxiv
import datetime
from sqlalchemy import create_engine, MetaData
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import Session
from website.database import ArxivEntry


def run_scrape(authors, db_file):
    engine = create_engine(db_file, echo=True, future=True)
    if not database_exists(engine.url):
        ArxivEntry.metadata.create_all(engine)

    prefix = 'http://arxiv.org/abs/'

    with Session(engine) as session:
        for author in authors:
            search = arxiv.Search(
                query="au:{}".format(author.strip()),
                max_results=float('inf'),
                sort_by=arxiv.SortCriterion.LastUpdatedDate,
            )
            for res in search.results():
                a = ArxivEntry(id=res.entry_id[len(prefix):],
                               url=res.entry_id,
                               title=res.title,
                               timestamp=res.updated,
                               summary=res.summary,
                               authors=", ".join((author.name for author in res.authors)),
                               image_url=None)
                instance = session.query(ArxivEntry).filter_by(id=a.id).first()
                if not instance:
                    session.add(a)
            session.commit()



if __name__ == "__main__":
    with open('authors.txt', 'r') as f:
        authors = f.readlines()
    run_scrape(authors, 'sqlite:///test.db')