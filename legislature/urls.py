from django.conf.urls import patterns, url

from legislature import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^about/$', views.about, name='about'),
    url(r'^debates/$', views.debates, name='section-list'),
    url(r'^debates/(?P<year>\d{4})/$', views.debates_by_year, name='section-list-by-year'),
)
