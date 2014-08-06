# OpenHouseNS

## Development

Follow the instructions in the [Python Quick Start Guide](https://github.com/opennorth/opennorth.ca/wiki/Python-Quick-Start%3A-OS-X) to install Homebrew (if OS X), Git, Python and virtualenvwrapper.

    mkvirtualenv openhousens
    git clone git@github.com:opennorth/openhousens.git
    cd openhousens

Install the requirements:

    pip install -r requirements.txt

If `pylibmc` fails to install, you may need to `export CFLAGS="-std=c99"`.

Create a database (`dropdb openhousens` if it already exists):

    createdb openhousens
    python manage.py syncdb --noinput

If you have Ruby, install the foreman gem:

    gem install foreman

And start the web app:

    foreman start

Otherwise, you can start the web app with:

    python manage.py runserver

### Importing Popolo data

Import organizations, people, posts and memberships:

    python manage.py load_popolo http://scrapers-ruby.herokuapp.com/

### Importing Akoma Ntoso data

Import a directory:

    python manage.py load_akomantoso --commit --instance=default --dir=akoma_ntoso/

Import a directory filtered by date. Filenames must be date-based:

    python manage.py load_akomantoso --commit --instance=default --dir=akoma_ntoso/ --start-date=yyyy-mm-dd

Import a file:

    python manage.py load_akomantoso --commit --instance=default --file=akoma_ntoso/2011-11-03_11-38.xml

### Enabling search

Rebuild the ElasticSearch index:

    python manage.py rebuild_index --noinput

We don't set `HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'` as it causes timeout errors in development.

### Abbreviations

Question Period section titles contain many abbreviations. Run this command to find new abbreviations:

    python manage.py abbreviations

If any new abbreviations are found, add them to `legislature/synonyms.py` so that they can be expanded in the views.

### Validations

All speeches should belong to a section:

```python
from speeches.models import Speech
Speech.objects.filter(section=None)
```

All sections should have speeches:

    from speeches.models import Section
    for section in Section.objects.filter(speech__section_id=None).filter(children__parent_id=None):
        print(section.get_ancestors[0].start_date, section.title)

All boundaries should match a membership label:

    import requests
    from popolo.models import Membership
    url = 'http://represent.opennorth.ca/boundaries/nova-scotia-electoral-districts/?limit=0'
    for boundary in requests.get(url).json()['objects']:
        try:
            Membership.objects.get(label='MLA for %s' % boundary['name'].replace('—', '-'))  # m-dash
        except Membership.DoesNotExist:
            print(boundary['name'])

## Deployment

You can use any of Heroku's ElasticSearch add-ons:

* [SearchBox](https://addons.heroku.com/searchbox)
* [Bonsai](https://addons.heroku.com/bonsai)
* [Found](https://addons.heroku.com/foundelasticsearch)

SayIt has three indices, and NS have over 10,000 speeches, so you need at least SearchBox Micro ($9) or Bonsai Staging ($10). You can alternatively run your own instance of ElasticSearch [on EC2, for example](http://www.elasticsearch.org/tutorials/elasticsearch-on-ec2/).

    heroku addons:add searchbox:micro
    heroku addons:add bonsai:staging
    heroku addons:add foundelasticsearch:chihuahua-standard

Set the ElasticSearch configuration variable using one of the following:

    heroku config:add ELASTICSEARCH_URL=`heroku config:get SEARCHBOX_URL`
    heroku config:add ELASTICSEARCH_URL=`heroku config:get BONSAI_URL`
    heroku config:add ELASTICSEARCH_URL=`heroku config:get FOUNDELASTICSEARCH_URL`

Add the SendGrid add-on for error reporting:

    heroku addons:add sendgrid

Add and [configure](https://devcenter.heroku.com/articles/flydata#s3-integration) the FlyData add-on to archive logs for later analysis:

    heroku addons:add flydata

Add the Memcachier add-on for caching:

    heroku addons:add memcachier

Enable the [`log-runtime-metrics`](https://devcenter.heroku.com/articles/log-runtime-metrics) feature to track memory consumption, in case `WEB_CONCURRENCY` needs to be adjusted:

    heroku labs:enable log-runtime-metrics

Add configuration variables (replace `YOUR-DJANGO-SECRET-KEY`):

    heroku config:set PRODUCTION=1
    heroku config:set WEB_CONCURRENCY=3
    heroku config:set PYTHONHASHSEED=random
    heroku config:set DJANGO_SECRET_KEY=YOUR-DJANGO-SECRET-KEY

You can [generate a secret key in Python](https://github.com/django/django/blob/master/django/core/management/commands/startproject.py):

```python
from django.utils.crypto import get_random_string
get_random_string(50, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
```

[Upgrade to the Hobby Basic plan](https://devcenter.heroku.com/articles/upgrade-heroku-postgres-with-pgbackups), since NS has over 10,000 speeches.

Setup the database (you can run `heroku pg:reset` to start over):

    heroku run python manage.py syncdb --noinput

Import Popolo and Akoma Ntoso data:

    heroku run python manage.py load_popolo http://scrapers-ruby.herokuapp.com/
    heroku run python manage.py load_akomantoso --commit --instance=default --dir=akoma_ntoso/

Rebuild the ElasticSearch index:

    heroku run python manage.py rebuild_index --noinput

Add the Scheduler add-on:

    heroku addons:add scheduler

[Schedule](https://scheduler.heroku.com/dashboard) the following job daily:

    python manage.py load_popolo http://scrapers-ruby.herokuapp.com/

## Bugs? Questions?

This repository is on GitHub: [http://github.com/opennorth/openhousens](http://github.com/opennorth/openhousens), where your contributions, forks, bug reports, feature requests, and feedback are greatly welcomed.

Copyright (c) 2014 Open North Inc., released under the MIT license
