from __future__ import division

import uuid
import datetime
import random

from django.contrib.syndication.views import Feed
from django.views.generic import TemplateView
from django.utils.feedgenerator import Atom1Feed, Rss201rev2Feed
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
import string
from .models import TestFeed, TestFeedItem


class ScrewedUpResponse(HttpResponse):
    def items(self):
        return [("lol\n\n!", "o\n\br\0")]  # Send an invalid header to the client. Messes stuff up


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
        self.simulate_issue = None

        if random.randint(0, 100) > 75 and "tryme" in request.GET:
            self.simulate_issue = random.choice(["500", "redirect", "non_xml",
                                                 "invalid_xml", "non_http",
                                                 "screwed_results", "future_dates"])

            if self.simulate_issue == "500":
                return HttpResponse("500 internal server error", status=500)
            elif self.simulate_issue == "redirect":
                return HttpResponseRedirect("http://google.com")
            elif self.simulate_issue == "non_xml":
                return HttpResponse("This is some non-xml content for you", content_type="text/plain")

        result = super(BaseFeed, self).__call__(request, *args, **kwargs)

        if self.simulate_issue == "invalid_xml":
            # Replace a bunch of characters in the response text
            resp_length = len(result.content)
            content = list(result.content)
            for i in xrange(int(resp_length / 10)):
                idx_to_change = random.randint(0, resp_length)
                content[idx_to_change] = random.choice(string.printable)

            result.content = "".join(content)
        elif self.simulate_issue == "non_http":
            return ScrewedUpResponse()

        return result

    def get_key(self, request, *args, **kwargs):
        raise NotImplementedError()

    def get_total_seconds(self, elapsed):
        return (elapsed.microseconds + (elapsed.seconds + elapsed.days*24*3600) * 1e6) / 1e6  # Python 2.6 compatability

    def get_object(self, request, *args, **kwargs):
        key = self.get_key(request, *args, **kwargs)
        obj, created = TestFeed.objects.get_or_create(key=key)

        if created:
            last_item = TestFeedItem.objects.create(feed=obj)
        else:
            last_item = obj.items.latest()

        trigger_time = kwargs.get("time", "30")

        create_trigger = min(max(int(trigger_time if trigger_time.isdigit() else "30"), 15), 60)

        # Work out how long it has been since we have created a post
        created_ago = (datetime.datetime.now() - last_item.created)

        if created_ago > datetime.timedelta(seconds=create_trigger):
            # Create a new item with a time between
            random_time = created_ago + datetime.timedelta(seconds=random.randint(1, int(self.get_total_seconds(created_ago))))
            TestFeedItem.objects.create(feed=obj, display_time=random_time)

        return obj

    def items(self, obj):
        items = obj.items
        if self.simulate_issue == "screwed_results":
            return items.order_by("?")[:10]

        return items.order_by("-created")[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content

    def item_link(self, item):
        return item.get_absolute_url()

    def item_guid(self, item):
        return item.id

    def item_pubdate(self, item):
        if self.simulate_issue == "future_dates":
            if random.randint(1, 2) == 2:
                return datetime.datetime.now() + datetime.timedelta(minutes=random.randint(0, 60))
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