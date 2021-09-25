from collections import defaultdict
import arxiv
import os
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists
from sqlalchemy.orm import Session
from website.database import ArxivEntry
import re
import json
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)


def get_authors_and_tags(dir):
    all_authors = set()
    author_tags = defaultdict(lambda: list())
    for filename in os.listdir(dir):
        with open(os.path.join(dir, filename), 'r') as f:
            for authorline in f.readlines():
                author_entries = [entry.strip() for entry in authorline.split(',') if entry.strip()]
                if len(author_entries):
                    author = author_entries.pop(0)
                    all_authors.add(author)
                    tags = author_entries
                    author_tags[author].append('author_list:{}'.format(os.path.splitext(filename)[0]))
                    author_tags[author].extend('author_tags:{}'.format(tag) for tag in tags)
    return all_authors, author_tags


def run_scrape(authors, authors_tags, db_file, strip_versions=True):
    def update_url(res, instance, **kwargs):
        if res.doi:
            url = doi_prefix + res.doi
        else:
            url = arxiv_prefix + res_id
        if url != instance.url:
            instance.url = url
    def update_timestamp(res, instance, **kwargs):
        if res.published != instance.timestamp:
            instance.timestamp = res.published
    def update_title(res, instance, **kwargs):
        if res.title != instance.title:
            instance.title = res.title
    def update_abstact(res, instance, **kwargs):
        abstract = res.summary.replace('\n', ' ')
        if abstract != instance.abstract:
            instance.abstract = abstract
    def update_authors(res, instance, **kwargs):
        authors = ", ".join((author.name for author in res.authors))
        if instance.authors != authors:
            instance.authors = authors
    def update_journal(res, instance, **kwargs):
        if instance.journal_ref != res.journal_ref:
            instance.journal_ref = res.journal_ref
    def update_doi(res, instance, **kwargs):
        if res.doi != instance.doi:
            instance.doi = res.doi
    def update_tags(res, instance, **kwargs):
        existing_tags = set()
        if instance.tags:
            existing_tags.update(tag.strip() for tag in instance.tags.split(',') if tag.strip())
        # Arxiv categories
        existing_tags.update('arxiv:{}'.format(cat) for cat in res.categories)

        # Author categories
        existing_tags.update(authors_tags[kwargs['author']])

        tags = ", ".join(sorted(existing_tags)) + ','
        if tags != instance.tags:
            instance.tags = tags
    def update_unstructured(res, instance, **kwargs):
        default_unstructured = '{"autoupdates": ["doi", "journal", "tags", "unstructured"]}'
        if instance.unstructured != default_unstructured:
            instance.unstructured = default_unstructured

    updaters = {
        'url': update_url,
        'timestamp': update_timestamp,
        'title': update_title,
        'abstract': update_abstact,
        'authors': update_authors,
        'journal': update_journal,
        'doi': update_doi,
        'tags': update_tags,
        'unstructured': update_unstructured
    }

    engine = create_engine(db_file, echo=False, future=True)
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
                query="au:{}".format(author),
                max_results=float('inf'),
                sort_by=arxiv.SortCriterion.LastUpdatedDate,
            )
            for res in search.results():
                res_id = process(res.entry_id[len(arxiv_prefix):])
                instance = session.query(ArxivEntry).filter_by(id=res_id).first()
                if not instance:
                    instance = ArxivEntry(id=res_id, hidden=False, autoupdate=True)
                    session.add(instance)
                autoupdates = []
                if instance.autoupdate:
                    autoupdates = updaters.keys()
                elif instance.unstructured:
                    try:
                        unstructured_data = json.loads(instance.unstructured)
                        if 'autoupdates' in unstructured_data:
                            autoupdates = list(unstructured_data['autoupdates'])
                    except json.decoder.JSONDecodeError:
                        pass
                    except Exception as e:
                        print("Unknown exception: {}".format(e))
                for updater in autoupdates:
                    if updater in updaters:
                        updaters[updater](res, instance, author=author)
                session.commit()


if __name__ == "__main__":
    authors, tags = get_authors_and_tags('authors')
    run_scrape(authors, tags, 'sqlite:///test.db')
