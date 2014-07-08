from django.conf.urls import patterns, include, url

from speeches.views import *

# This file is maybe a mistake, given that we can easily go out of sync with
# SayIt's urls.py. There's no harm in using SayIt's urls.py; we just end up
# having a bunch of URLs that should 404 in our case. (2014-07-07)
# @see https://github.com/mysociety/sayit/blob/master/speeches/urls.py

# SayIt URLs we will never use are omitted. URLs that we override with the
# legislature app are commented out.
speeches_patterns = [
    # url(r'^$', InstanceView.as_view(), name='home'),

    url(r'^(?P<path>speaker)/?$', AddAnSRedirectView.as_view()),
    url(r'^(?P<path>speech)/?$', AddAnSRedirectView.as_view(suffix='es')),

    url(r'^search/', lambda request: InstanceSearchView()(request), name='haystack_search'),

    url(r'^speech/(?P<pk>\d+)$', SpeechView.as_view(), name='speech-view'),

    url(r'^speakers$', SpeakerList.as_view(), name='speaker-list'),
    url(r'^speaker/(?P<slug>.+)$', SpeakerView.as_view(), name='speaker-view'),

    url(r'^sections/(?P<pk>\d+)$', SectionView.as_view(), name='section-id-view'),
    # url(r'^speeches$', SectionList.as_view(), name='section-list'),

    url(r'^(?P<full_slug>.+)$', SectionView.as_view(), name='section-view'),
]

urlpatterns = patterns('',
    (r'', include('legislature.urls', namespace='legislature', app_name='legislature')),
    (r'', include(speeches_patterns, namespace='sayit', app_name='speeches')),
    # (r'', include('speeches.urls', namespace='sayit', app_name='speeches')),
)
