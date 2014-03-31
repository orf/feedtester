from django.conf.urls import patterns, url
from django.views.generic import DetailView

from .views import KeyFeed, CookieFeed, Homepage
from .models import TestFeedItem


urlpatterns = patterns('',
                       url('^$', Homepage.as_view(template_name="index.html" )),
                       url('^item/(?P<id>\d+)', DetailView.as_view(pk_url_kwarg="id", model=TestFeedItem), name="view"),
                       url('^feed/(?P<feed_type>(rss|atom))/cookie', CookieFeed(), name="cookie"),
                       url('^feed/(?P<feed_type>(rss|atom))/(?P<key>\S+)$', KeyFeed(), name="key"),
                       )
