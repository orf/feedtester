from django.conf.urls import patterns, url
from .views import KeyFeed, CookieFeed, Homepage
from django.views.generic import DetailView
from .models import TestFeedItem
import uuid

urlpatterns = patterns('',
                       url('^$', Homepage.as_view(template_name="index.html" )),
                       url('^item/(?P<id>\d+)', DetailView.as_view(pk_url_kwarg="id", model=TestFeedItem), name="view"),
                       url('^feed/cookie', CookieFeed(), name="cookie"),
                       url('^feed/(?P<key>\S+)$', KeyFeed(), name="key"),
                       )
