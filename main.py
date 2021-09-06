import website
import config
import os


app = website.create_app(config, make_db=False)


# This is only used when running locally.
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=False)