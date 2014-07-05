from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
  url(r'^admin/', include(admin.site.urls)),
  url(r'^speeches/', include('speeches.urls', namespace='sayit', app_name='speeches')),
)
