# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FlippaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    type_= scrapy.Field()
    monetization = scrapy.Field()
    net = scrapy.Field()
    price = scrapy.Field()
    monthly_net = scrapy.Field()
    age_of_site = scrapy.Field()
    site_type = scrapy.Field()
    multiple = scrapy.Field()
    platform= scrapy.Field()
    gross_rev = scrapy.Field()
    page_views = scrapy.Field()
    unique_visits = scrapy.Field()
