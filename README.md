# OpenHouseNS

## Development

Follow the instructions in the [Python Quick Start Guide](https://github.com/opennorth/opennorth.ca/wiki/Python-Quick-Start%3A-OS-X) to install Homebrew, Git, Python and virtualenv.

    mkvirtualenv openhousens
    git clone git@github.com:opennorth/openhousens.git
    cd openhousens

Install the requirements:

    pip install -r requirements.txt

Create a database (`openhousens pupa` if it already exists):

    dropdb openhousens
    createdb openhousens
    python manage.py syncdb --noinput

Install the foreman gem:

    gem install foreman

Start the web app:

    foreman start

## Deployment

You can use any of Heroku's ElasticSearch add-ons [SearchBox](https://addons.heroku.com/searchbox), [Bonsai](https://addons.heroku.com/bonsai) or [Found](https://addons.heroku.com/foundelasticsearch). SayIt has three indices, and you have over 10,000 speeches, so you need at least Bonsai Micro or Bonsai Staging. You can alternatively run your own instance of ElasticSearch - [on EC2, for example](http://www.elasticsearch.org/tutorials/elasticsearch-on-ec2/).

    heroku addons:add searchbox:micro
    heroku addons:add bonsai:staging
    heroku addons:add foundelasticsearch:chihuahua-standard

Set the ElasticSearch configuration variable using one of the following:

    heroku config:add ELASTICSEARCH_URL=`heroku config:get SEARCHBOX_URL`
    heroku config:add ELASTICSEARCH_URL=`heroku config:get BONSAI_URL`
    heroku config:add ELASTICSEARCH_URL=`heroku config:get FOUNDELASTICSEARCH_URL`

Add configuration variables (replace `YOUR-SECRET-KEY`):

    heroku config:set PRODUCTION=1
    heroku config:set DJANGO_SECRET_KEY=YOUR-DJANGO-SECRET-KEY

SayIt requires the `compass` and `zurb-foundation` gems to collect static files, which would take a lot of effort to run on Heroku, so instead we collect and commit static files.

    heroku config:set DISABLE_COLLECTSTATIC=1

You can [generate a secret key in Python](https://github.com/django/django/blob/master/django/core/management/commands/startproject.py):

```python
from django.utils.crypto import get_random_string
get_random_string(50, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
```

Setup the database (replace `DATABASE`):

    heroku pg:reset DATABASE
    heroku run python manage.py syncdb --noinput

## Bugs? Questions?

This repository is on GitHub: [http://github.com/opennorth/openhousens](http://github.com/opennorth/openhousens), where your contributions, forks, bug reports, feature requests, and feedback are greatly welcomed.

Copyright (c) 2014 Open North Inc., released under the MIT license
