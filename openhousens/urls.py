from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
  url(r'^speeches/', include('speeches.urls', namespace='sayit', app_name='speeches')),
)
