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

def run(db_file, img_path_prefix='website',
        thumbnail_location='website/static/img/thumbnails',
        thumbnail_url='static/img/thumbnails'):
    engine = create_engine(db_file, echo=False, future=True)
    if not database_exists(engine.url):
        return

    with Session(engine) as session:
        all_to_check = session.query(ArxivEntry)\
            .filter(ArxivEntry.image_url.startswith('static/img/')) \
            .filter(sqlalchemy.not_(ArxivEntry.image_url.startswith('static/img/thumbnails'))) \
            .all()
        for entry in all_to_check:
            print(entry.image_url)
            # Now make thumbnail
            try:
                basename = os.path.basename(entry.image_url)
                im = Image.open(os.path.join(img_path_prefix, entry.image_url))
                im.thumbnail((256,256), Image.ANTIALIAS)
                thumbnail_path = os.path.join(thumbnail_location, basename)
                im.save(thumbnail_path)
                entry.image_url = os.path.join(thumbnail_url, basename)
            except IOError:
                print("cannot create thumbnail for {}".format(entry.image_url))
        session.commit()

if __name__ == "__main__":
    run('sqlite:///test.db')