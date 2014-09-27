# OpenHouseNS: Deployment

## Configuration variables

Add configuration variables (replace `REPLACE`):

    # Change the environment to production.
    heroku config:set PRODUCTION=1
    # Control the number of Gunicorn workers.
    heroku config:set WEB_CONCURRENCY=3
    # Set PYTHONHASHSEED as recommended by Django.
    heroku config:set PYTHONHASHSEED=random
    # Override the secret key that appears in GitHub.
    heroku config:set DJANGO_SECRET_KEY=REPLACE
    # Enable access to the remote Akoma Ntoso files.
    # These variables are automatically read by boto.
    heroku config:set AWS_ACCESS_KEY_ID=REPLACE
    heroku config:set AWS_SECRET_ACCESS_KEY=REPLACE

You can [generate a secret key in Python](https://github.com/django/django/blob/master/django/core/management/commands/startproject.py):

```python
from django.utils.crypto import get_random_string
get_random_string(50, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
```

## Database

[Upgrade to the Hobby Basic plan](https://devcenter.heroku.com/articles/upgrade-heroku-postgres-with-pgbackups), since NS has over 10,000 speeches.

Setup the database (you can run `heroku pg:reset` to start over):

    heroku run python manage.py migrate --noinput

## Add-ons

Enable the [`log-runtime-metrics`](https://devcenter.heroku.com/articles/log-runtime-metrics) feature to track memory consumption, in case `WEB_CONCURRENCY` (above) needs to be adjusted:

    heroku labs:enable log-runtime-metrics

Add and [configure](https://devcenter.heroku.com/articles/flydata#s3-integration) the FlyData add-on to archive logs for later analysis:

    heroku addons:add flydata

Add the SendGrid add-on for error reporting, the Memcachier add-on for caching and the Scheduler add-on:

    heroku addons:add sendgrid
    heroku addons:add memcachier
    heroku addons:add scheduler

[Schedule](https://scheduler.heroku.com/dashboard) the following jobs daily:

    python manage.py load_popolo http://scrapers-ruby.herokuapp.com/
    python manage.py load_akomantoso_aws --commit --instance=default --dir=http://logs.openhousens.ca.s3.amazonaws.com/akoma_ntoso --no-clobber --start-date `date +%Y-%m-%d`
    python manage.py rebuild_index --noinput

### ElasticSearch

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

## Data

Import Popolo and Akoma Ntoso data, and rebuild the ElasticSearch index:

    heroku run python manage.py load_popolo http://scrapers-ruby.herokuapp.com/
    heroku run python manage.py load_akomantoso --commit --instance=default --dir=akoma_ntoso/
    heroku run python manage.py rebuild_index --noinput

## Scrapers

Deploy [scrapers-ca-ruby](https://github.com/opennorth/scrapers-ca-ruby/#deployment) and schedule:

    ruby ca_ns/scraper.rb --pipelined -q -t people
    ruby ca_ns/scraper.rb --pipelined -q -a scrape -a import -a akoma_ntoso -- down-to `date +%Y-%m-%d` no-clobber 1
