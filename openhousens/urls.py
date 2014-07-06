from django.conf.urls import patterns, include, url
from django.contrib import admin

from speeches.views import *

speeches_patterns = [
  url(r'^$', InstanceView.as_view(), name='home'),
  url(r'^(?P<path>speaker)/?$', AddAnSRedirectView.as_view()),
  url(r'^(?P<path>speech)/?$', AddAnSRedirectView.as_view(suffix='es')),
  url(r'^search/', lambda request: InstanceSearchView()(request), name='haystack_search'),
  url(r'^speech/(?P<pk>\d+)$', SpeechView.as_view(), name='speech-view'),
  url(r'^speakers$', SpeakerList.as_view(), name='speaker-list'),
  url(r'^speaker/(?P<slug>.+)$', SpeakerView.as_view(), name='speaker-view'),
  url(r'^sections/(?P<pk>\d+)$', SectionView.as_view(), name='section-id-view'),
  url(r'^speeches$', SectionList.as_view(), name='section-list'),
  url(r'^(?P<full_slug>.+)\.an$', SectionViewAN.as_view(), name='section-view'),
  url(r'^(?P<full_slug>.+)$', SectionView.as_view(), name='section-view'),
]

urlpatterns = patterns('',
  url(r'^admin/', include(admin.site.urls)),
  url(r'^speeches/', include(speeches_patterns, namespace='sayit', app_name='speeches')),
)
