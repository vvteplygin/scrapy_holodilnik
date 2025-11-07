# -*- coding: utf-8 -*-
import gc
import re
import json
import time

import boto3
import socket
import logging
import urllib.request
from scrapy import signals, Request
from pydispatch import dispatcher
from bhfutils.crawler.items import ProductDetailsResponseItem
from bhfutils.crawler.spiders.redis_spider import RedisSpider


class HolodilnikProductDetailsSpider(RedisSpider):
    idle_state_counter = 0
    spider_state = 'initial'

    name = 'HolodilnikProductDetails'
    allowed_domains = ['holodilnik.ru']

    # def start_requests(self):
    #     yield Request('https://www.holodilnik.ru/small_domestic/hoods/korting/khc_6839_nx/',
    #                   callback=self.parse,
    #                   meta={
    #                       'appid': 'product_details_ru',
    #                       'spiderid': 'HolodilnikProductDetails',
    #                       'expires': 0, 'priority': 1,
    #                       'crawlid': 'f75111d9-3e2f-43f0-970a-112021026631',
    #                       'domain_max_pages': 100,
    #                       'attrs': {
    #                           'groupId': 100
    #                       }
    #                   }, dont_filter=True)

    def __init__(self, *args, **kwargs):
        gc.set_threshold(100, 3, 3)

        logging.getLogger('kazoo').setLevel(logging.WARNING)
        logging.getLogger('kafka').setLevel(logging.WARNING)
        logging.getLogger('boto3').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('selenium').setLevel(logging.WARNING)
        logging.getLogger('botocore').setLevel(logging.WARNING)
        logging.getLogger('scrapy.core.scraper').setLevel(logging.WARNING)

        dynamo_db = boto3.resource('dynamodb')
        self.spiders_table = dynamo_db.Table('BhfSpiders')
        try:
            self.public_ip = urllib.request.urlopen("http://checkip.amazonaws.com",
                                                    timeout=5).read().decode('utf-8').rstrip()
            self.private_ip = socket.gethostbyname(socket.gethostname())
        except:
            self.public_ip = "127.0.0.1"
            self.private_ip = "127.0.0.1"
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        dispatcher.connect(self.log_idle, signals.spider_idle)
        dispatcher.connect(self.log_working, signals.request_scheduled)
        super(HolodilnikProductDetailsSpider, self).__init__(*args, **kwargs)

    def sync_spider_state(self, state):
        self.spiders_table.put_item(
            Item={
                'public_ip': self.public_ip,
                'private_ip': self.private_ip,
                'name': 'HolodilnikProductDetails',
                'status': state,
                'status_date': int(round(time.time() * 1000)),
            }
        )

    def spider_opened(self):
        self.sync_spider_state('opened')

    def log_working(self):
        self.idle_state_counter = 0
        if self.spider_state != 'working':
            self.spider_state = 'working'
            self.sync_spider_state('working')

    def log_idle(self):
        if self.spider_state != 'idle':
            self.idle_state_counter = self.idle_state_counter + 1
            if self.idle_state_counter > 3:
                self.spider_state = 'idle'
                self.idle_state_counter = 0
                self.sync_spider_state('idle')

    def spider_closed(self):
        self.sync_spider_state('closed')

    def parse(self, response, **kwargs):
        title = response.css('meta[itemprop="name"]').attrib['content']
        brand = response.css('div.product-brand strong::text').get()

        images = response.css('div.card-product-img div.card-product-img__body div[data-fancybox="images"]')
        images = ['https:'+x.attrib['data-src'] for x in images]

        details = {}
        detail_list = response.css('div.det-content-block div.params-list__item')
        for detail in detail_list:
            key = detail.css('div.params-list__item-name::text').get().strip()
            if not key:
                key = detail.css('div.params-list__item-name span::text').get()

            key = key.strip()
            value = detail.css('div.params-list__item-value span::text').get()
            value = value.strip() if value else 'Нет'
            details[key] = value

        desc = response.css('#full_description::text').getall()
        desc = '\n'.join([x.strip() for x in desc if x.strip()])

        item = ProductDetailsResponseItem()
        # populated from response.meta
        item['appid'] = response.meta['appid']
        item['crawlid'] = response.meta['crawlid']
        item['url'] = response.request.url
        item['responseUrl'] = response.url
        item['statusCode'] = response.status
        item["playgroundId"] = 3
        item["groupId"] = response.meta["attrs"]["groupId"]
        item["productUrl"] = response.request.url
        item["imageUrls"] = images
        item["name"] = title
        item["details"] = details
        item["brandName"] = brand
        item["description"] = desc
        yield item
