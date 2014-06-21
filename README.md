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

Add configuration variables (replace `YOUR-SECRET-KEY` and `DATABASE`):

    heroku config:set DJANGO_SECRET_KEY=YOUR-DJANGO-SECRET-KEY

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
