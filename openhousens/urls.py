from django.conf.urls import patterns, include, url

from speeches.search import InstanceSearchView
from speeches.views import *

# This file is maybe a mistake, given that we can easily go out of sync with
# SayIt's urls.py. There's no harm in using SayIt's urls.py; we just end up
# having a bunch of URLs that should 404 in our case. (2014-07-07)
# @see https://github.com/mysociety/sayit/blob/master/speeches/urls.py

# SayIt URLs we will never use are omitted, as well as URLs that we override.
speeches_patterns = [
    url(r'^search/', lambda request: InstanceSearchView()(request), name='haystack_search'),

    url(r'^(?P<path>speaker)/?$', AddAnSRedirectView.as_view()),
    url(r'^speakers$', SpeakerList.as_view(), name='speaker-list'),
    url(r'^speaker/(?P<slug>.+)$', SpeakerView.as_view(), name='speaker-view'),
]

urlpatterns = patterns('',
    (r'', include('legislature.urls', namespace='legislature', app_name='legislature')),
    (r'', include(speeches_patterns, namespace='sayit', app_name='speeches')),
)
