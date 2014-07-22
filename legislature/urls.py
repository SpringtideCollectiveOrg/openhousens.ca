from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page

from legislature import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^about/$', views.about, name='about'),
    url(r'^people/$', views.people, name='speaker-list'),
    url(r'^people/(?P<slug>[-_\w]+)$', views.person, name='speaker-view'),
    url(r'^debates/$', views.debates, name='section-list'),
    url(r'^debates/(?P<year>\d{4})/$', views.debates_by_year, name='section-list-by-year'),
    url(r'^debates/(?P<year>\d{4})/(?P<month>\d{1,2})/$', views.debates_by_month, name='section-list-by-month'),
    url(r'^debates/(?P<slug>\D[-_\w]+)$', views.debate, name='section-view'),
    url(r'^bills/$', cache_page(86400)(views.bills), name='bill-list'),
    url(r'^bills/(?P<slug>[-_\w.]+)$', cache_page(86400)(views.bill), name='bill-view'),
    url(r'^search/', lambda request: views.CustomSearchView()(request), name='haystack_search'),
)
