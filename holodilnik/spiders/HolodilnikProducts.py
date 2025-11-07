# -*- coding: utf-8 -*-
import gc
import time

import boto3
import socket
import logging
import urllib.request
import urllib.parse

from pydispatch import dispatcher
from scrapy import signals, Request
from scrapy.http import HtmlResponse
from bhfutils.crawler.items import ProductResponseItem
from bhfutils.crawler.spiders.redis_spider import RedisSpider


class HolodilnikProductsSpider(RedisSpider):
    spider_state = 'initial'

    name = 'HolodilnikProducts'
    allowed_domains = ['holodilnik.ru']

    # def start_requests(self):
    #     yield Request('https://www.holodilnik.ru/small_domestic/hoods/',
    #                   callback=self.parse,
    #                   meta={
    #                       'appid': 'products_ru',
    #                       'spiderid': 'HolodilnikProducts',
    #                       'expires': 0, 'priority': 1,
    #                       'crawlid': 'f75111d9-3e2f-43f0-970a-112021026631',
    #                       'domain_max_pages': 100,
    #                       'attrs': {
    #                           'page': 1,
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
        self.spider_messages_table = dynamo_db.Table('BhfSpiderMessages')
        try:
            self.public_ip = urllib.request.urlopen("http://checkip.amazonaws.com",
                                                    timeout=5).read().decode('utf-8').rstrip()
            self.private_ip = socket.gethostbyname(socket.gethostname())
        except:
            self.public_ip = "127.0.0.1"
            self.private_ip = "127.0.0.1"
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        dispatcher.connect(self.log_error, signals.spider_error)
        dispatcher.connect(self.log_error, signals.item_error)
        dispatcher.connect(self.log_idle, signals.spider_idle)
        dispatcher.connect(self.log_working, signals.request_scheduled)
        super(HolodilnikProductsSpider, self).__init__(*args, **kwargs)

    def log_spider_message(self, message):
        self.spider_messages_table.put_item(
            Item={
                'spiderId': self.public_ip,
                'messageDate': int(round(time.time() * 1000)),
                'name': 'HolodilnikProducts',
                'message': message,
            }
        )

    def sync_spider_state(self, state):
        self.spiders_table.put_item(
            Item={
                'public_ip': self.public_ip,
                'private_ip': self.private_ip,
                'name': 'HolodilnikProducts',
                'status': state,
                'status_date': int(round(time.time() * 1000)),
            }
        )

    def spider_opened(self):
        self.sync_spider_state('opened')

    def log_working(self):
        if self.spider_state != 'working':
            self.spider_state = 'working'
            self.sync_spider_state('working')

    def log_idle(self):
        if self.spider_state != 'idle':
            self.spider_state = 'idle'
            self.sync_spider_state('idle')

    def spider_closed(self):
        self.sync_spider_state('closed')

    def log_error(self, failure):
        self.log_spider_message(failure.getErrorMessage())

    def parse(self, response: HtmlResponse, **kwargs):
        captcha = response.css('div.g-recaptcha')
        if captcha:
            response.request.dont_filter = True
            response.request.meta.update({'dont_retry': True})
            yield response.request
            return

        base = 'https://www.holodilnik.ru'
        prods = response.css('div#view-row div.preview-product')
        for prod in prods:
            prod_url = prod.css('div.product-name a').attrib['href']
            price = prod.css('div.price div.price__value::text').get()
            if not price: continue

            for i in '₽\xa0 ':
                price = price.replace(i, '')
            price = int(price.strip())

            item = ProductResponseItem()
            # populated from response.meta
            item['appid'] = response.meta['appid']
            item['crawlid'] = response.meta['crawlid']
            item['url'] = response.request.url
            item['responseUrl'] = response.url
            item['statusCode'] = response.status
            item["playgroundId"] = 3
            item["groupId"] = response.meta["attrs"]["groupId"]
            item["productUrl"] = base + prod_url
            item["price"] = price
            yield item

        pages = response.css('ul.pagination li.page-next a.page-link')
        if pages:
            yield response.follow(base + pages.attrib['href'])
