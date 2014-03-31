from django.db import models
from django.contrib.webdesign import lorem_ipsum
from django.core.urlresolvers import reverse


class TestFeed(models.Model):
    key = models.TextField(primary_key=True)
    created = models.DateField(auto_now_add=True)


class TestFeedItem(models.Model):
    feed = models.ForeignKey(TestFeed, related_name="items")
    created = models.DateTimeField(auto_now_add=True)
    display_time = models.DateTimeField(auto_now_add=True)
    title = models.TextField(default=lorem_ipsum.sentence)
    content = models.TextField(default=lambda: "\n".join(lorem_ipsum.paragraphs(2)))

    def get_absolute_url(self):
        return reverse("feeds:view", args=[self.id])

    class Meta:
        get_latest_by = "created"