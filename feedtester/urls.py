from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url('^', include('feeds.urls', namespace="feeds")),
)
