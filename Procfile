# @see https://devcenter.heroku.com/articles/getting-started-with-django#declare-process-types-with-procfile
# @see https://devcenter.heroku.com/articles/python-gunicorn
# @see http://docs.gunicorn.org/en/latest/settings.html
web: gunicorn openhousens.wsgi --workers $WEB_CONCURRENCY
