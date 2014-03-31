from django.contrib.syndication.views import Feed
from .models import TestFeed, TestFeedItem
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
import uuid
import datetime


class Homepage(TemplateView):
    def get_context_data(self, **kwargs):
        ctx = super(Homepage, self).get_context_data(**kwargs)
        ctx.update({"uuid": uuid.uuid4})
        return ctx


class BaseFeed(Feed):
    title = "A feed"
    description = "A feed description"

    def get_key(self, request, *args, **kwargs):
        raise NotImplementedError()

    def get_object(self, request, *args, **kwargs):
        key = self.get_key(request, *args, **kwargs)
        obj, created = TestFeed.objects.get_or_create(key=key)

        if created:
            last_item = TestFeedItem.objects.create(feed=obj)
        else:
            last_item = obj.items.latest()

        create_trigger = min(max(int(kwargs.get("time", "30")), 15), 60)

        if (datetime.datetime.now() - last_item.created) > datetime.timedelta(seconds=create_trigger):
            # Create a new item
            TestFeedItem.objects.create(feed=obj)

        return obj

    def items(self, obj):
        return obj.items.order_by("-created")[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content

    def item_pubdate(self, item):
        return item.created

    def link(self, obj):
        return reverse("feeds:key", args=[obj.key])


class CookieFeed(BaseFeed):
    def get_key(self, request, *args, **kwargs):
        if "feed_id" not in request.session:
            request.session["feed_id"] = uuid.uuid4().hex
        return request.session["feed_id"]


class KeyFeed(BaseFeed):
    def get_key(self, request, *args, **kwargs):
        return kwargs["key"]