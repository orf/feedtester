Feed creator
============

Feed creator is a simple Django service that generates persistent updating RSS feeds.

## Usage
A feed can be accessed by using any string as a key by accessing this url: /feed/KEY. For example: /feed/3aba48e842bf49d086249074a663ba6c

If you don't want to specify a key you can request /feeds/cookie. This will set a cookie which you will need to keep and re-send) with each request.

## Options
By default a new item will be created when the feed is requested, if one hasn't been created in the last 30 seconds. You can pass an integer between 15 and 60 in the time parameter. To create a feed with a new entry every 20 seconds request this URL: /feed/ead99fc85b7442edaa7e41911bdd8876?time=20