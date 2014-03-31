import uuid
import datetime
import random

from django.contrib.syndication.views import Feed
from django.views.generic import TemplateView
from django.utils.feedgenerator import Atom1Feed, Rss201rev2Feed
from django.core.urlresolvers import reverse

from .models import TestFeed, TestFeedItem


class Homepage(TemplateView):
    def get_context_data(self, **kwargs):
        ctx = super(Homepage, self).get_context_data(**kwargs)
        ctx.update({"uuid": uuid.uuid4})
        return ctx


class BaseFeed(Feed):
    title = "A feed"
    description = "A feed description"

    def __call__(self, request, *args, **kwargs):
        self.feed_type_name = kwargs["feed_type"]
        self.feed_type = Rss201rev2Feed if self.feed_type_name == "rss" else Atom1Feed
        return super(BaseFeed, self).__call__(request, *args, **kwargs)

    def get_key(self, request, *args, **kwargs):
        raise NotImplementedError()

    def get_object(self, request, *args, **kwargs):
        key = self.get_key(request, *args, **kwargs)
        obj, created = TestFeed.objects.get_or_create(key=key)

        if created:
            last_item = TestFeedItem.objects.create(feed=obj)
        else:
            last_item = obj.items.latest()

        trigger_time = kwargs.get("time", "30")

        create_trigger = min(max(int(trigger_time if trigger_time.isdigit() else "30"), 15), 60)
        created_ago = (datetime.datetime.now() - last_item.created)
        if created_ago > datetime.timedelta(seconds=create_trigger):
            # Create a new item
            random_time = created_ago + datetime.timedelta(seconds=random.randint(1, int(created_ago.total_seconds())))
            TestFeedItem.objects.create(feed=obj, display_time=random_time)

        return obj

    def items(self, obj):
        return obj.items.order_by("-created")[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content

    def item_pubdate(self, item):
        return item.display_time

    def link(self, obj):
        return reverse("feeds:key", args=[self.feed_type_name, obj.key])


class CookieFeed(BaseFeed):
    def get_key(self, request, *args, **kwargs):
        if "feed_id" not in request.session:
            request.session["feed_id"] = uuid.uuid4().hex
        return request.session["feed_id"]


class KeyFeed(BaseFeed):
    def get_key(self, request, *args, **kwargs):
        return kwargs["key"]