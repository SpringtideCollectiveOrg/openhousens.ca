# OpenHouseNS: Development

Follow the instructions in the [Python Quick Start Guide](https://github.com/opennorth/wiki/wiki/Python-Quick-Start%3A-OS-X) to install Homebrew (if OS X), Git, Python and virtualenvwrapper.

    mkvirtualenv openhousens
    git clone git@github.com:opennorth/openhousens.git
    cd openhousens

Install the requirements:

    pip install -r requirements.txt

If `pylibmc` fails to install, you may need to `export CFLAGS="-std=c99"`.

Create a database (`dropdb openhousens` if it already exists):

    createdb openhousens
    python manage.py migrate --noinput

If you have Ruby, install the foreman gem:

    gem install foreman

And start the web app as it would on Heroku:

    foreman start

Otherwise, you can start the web app with:

    python manage.py runserver

## Import Popolo data

Import organizations, people, posts and memberships:

    python manage.py load_popolo http://openhousens-scrapers.herokuapp.com/

## Import Akoma Ntoso data

Import a directory:

    python manage.py load_akomantoso --commit --instance=default --dir=akoma_ntoso/

Import a directory filtered by date. Filenames must be date-based:

    python manage.py load_akomantoso --commit --instance=default --dir=akoma_ntoso/ --start-date=yyyy-mm-dd

Import a file:

    python manage.py load_akomantoso --commit --instance=default --file=akoma_ntoso/2011-11-03_11-38.xml

## Enable search

Rebuild the ElasticSearch index:

    python manage.py rebuild_index --noinput

We don't set `HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'` as it causes timeout errors in development.
