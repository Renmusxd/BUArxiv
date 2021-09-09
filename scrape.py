import arxiv
import datetime
from sqlalchemy import create_engine, MetaData
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import Session
from website.database import ArxivEntry
import re


def run_scrape(authors, db_file, strip_versions=True):
    engine = create_engine(db_file, echo=True, future=True)
    if not database_exists(engine.url):
        ArxivEntry.metadata.create_all(engine)

    arxiv_prefix = 'http://arxiv.org/abs/'
    doi_prefix = 'http://doi.org/'

    if strip_versions:
        pat = re.compile('v\d+$')
        process = lambda s: pat.sub('', s)
    else:
        process = lambda s: s

    with Session(engine) as session:
        for author in authors:
            search = arxiv.Search(
                query="au:{}".format(author.strip()),
                max_results=float('inf'),
                sort_by=arxiv.SortCriterion.LastUpdatedDate,
            )
            for res in search.results():
                res_id = process(res.entry_id[len(arxiv_prefix):])
                instance = session.query(ArxivEntry).filter_by(id=res_id).first()
                if not instance:
                    if res.doi:
                        url = doi_prefix + res.doi
                    else:
                        url = arxiv_prefix + res_id
                    a = ArxivEntry(id=res_id,
                                   url=url,
                                   title=res.title,
                                   timestamp=res.published,
                                   abstract=res.summary.replace('\n', ' '),
                                   authors=", ".join((author.name for author in res.authors)),
                                   journal_ref=res.journal_ref,
                                   doi=res.doi,
                                   image_url=None,
                                   tags=", ".join(res.categories),
                                   autoupdate=True,
                                   hidden=False)
                    session.add(a)
                elif instance.autoupdate:
                    if res.doi:
                        url = doi_prefix + res.doi
                    else:
                        url = arxiv_prefix + res_id
                    instance.url = url
                    instance.timestamp = res.published
                    instance.title = res.title
                    instance.abstract = res.summary.replace('\n', ' ')
                    instance.authors = ", ".join((author.name for author in res.authors))
                    instance.timestamp = res.published
                    instance.journal_ref = res.journal_ref
                    instance.doi = res.doi
                    instance.tags = ", ".join(res.categories)
            session.commit()


if __name__ == "__main__":
    with open('authors.txt', 'r') as f:
        authors = f.readlines()
    run_scrape(authors, 'sqlite:///test.db')