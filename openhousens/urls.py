from django.conf.urls import patterns, include

urlpatterns = patterns('',
    (r'', include('legislature.urls', namespace='legislature', app_name='legislature')),
)
