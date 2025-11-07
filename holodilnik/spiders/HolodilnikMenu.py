# -*- coding: utf-8 -*-
import logging

from scrapy import Request
from bhfutils.crawler.items import MenuResponseItem
from bhfutils.crawler.spiders.redis_spider import RedisSpider


class HolodilnikMenuSpider(RedisSpider):
    name = 'HolodilnikMenu'
    allowed_domains = ['holodilnik.ru']

    def start_requests(self):
        yield Request('https://www.holodilnik.ru/',
                      callback=self.parse,
                      meta={
                          'appid': 'menu_ru',
                          'spiderid': 'HolodilnikMenu',
                          'expires': 0, 'priority': 1,
                          'crawlid': 'f75111d9-3e2f-43f0-970a-112021026632',
                          'domain_max_pages': 100
                      }, dont_filter=True)

    def __init__(self, *args, **kwargs):
        logging.getLogger('kazoo').setLevel(logging.WARNING)
        logging.getLogger('kafka').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('scrapy.core.scraper').setLevel(logging.WARNING)
        super(HolodilnikMenuSpider, self).__init__(*args, **kwargs)

    def parse(self, response, cat_list=None, **kwargs):
        if cat_list:
            js_data = response.json()

            for menu in js_data:
                menu_title = cat_list.pop(0)
                for cat in menu:
                    cat_title = cat['title']
                    url = 'https://www.holodilnik.ru' + cat['href']

                    # capture response
                    item = MenuResponseItem()
                    # populated from response.meta
                    item['appid'] = response.meta['appid']
                    item['crawlid'] = response.meta['crawlid']
                    item['url'] = response.request.url
                    item['responseUrl'] = response.url
                    item['statusCode'] = response.status
                    item["playgroundId"] = 3
                    item["groupCategoryName"] = menu_title
                    item["groupName"] = cat_title
                    item["groupUrl"] = url
                    yield item

        else:
            cat_list = []
            cats = response.css('div.site-burger__catalog-section-item')
            for cat in cats:
                if cat.attrib['id'] in ['navBrands', 'navDiscounted']:
                    continue

                title = cat.css('.site-burger__frame-title::text').getall()[-1].strip()
                cat_list.append(title)

            yield response.follow('https://www.holodilnik.ru/i/cache/cats_menu2/categories_1.json', cb_kwargs={'cat_list': cat_list})
