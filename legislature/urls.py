from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page

from legislature import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^about/$', views.about, name='about'),
    url(r'^donate/$', views.about, name='donate'),
    url(r'^people/$', views.people, name='speaker-list'),
    url(r'^people/(?P<slug>[-_\w]+)/$', views.person, name='speaker-view'),
    url(r'^people/(?P<slug>[-_\w]+)/notices/$', views.person_notices, name='speaker-view-notices'),
    url(r'^debates/$', views.debates, name='section-list'),
    url(r'^debates/(?P<year>\d{4})/$', views.debates_by_year, name='section-list-by-year'),
    url(r'^debates/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.debates_by_month, name='section-list-by-month'),
    # It's possible for two hansards to have the same date, so we use slugs.
    url(r'^debates/(?P<slug>\D[-_\w]+)/$', views.debate, name='section-view'),
    url(r'^written-notices/(?P<slug>\D[-_\w]+)/$', views.notices, name='notices-view'),
    # OpenParliament.ca uses a `sequence` field to determine the page on which
    # the speech appers. SayIt lists all speeches in a section. Until SayIt adds
    # a `sequence` field to the Speech model, we put all speeches on one page
    # when linking to a speech.
    url(r'^debates/(?P<slug>\D[-_\w]+)/single-page/$', views.debate_single_page, name='section-view-single-page'),
    url(r'^written-notices/(?P<slug>\D[-_\w]+)/single-page/$', views.notices_single_page, name='notices-view-single-page'),
    url(r'^bills/$', cache_page(86400)(views.bills), name='bill-list'),
    url(r'^bills/(?P<slug>[-_\w.]+)/$', cache_page(86400)(views.bill), name='bill-view'),
    url(r'^search/', lambda request: views.CustomSearchView()(request), name='haystack_search'),
)
