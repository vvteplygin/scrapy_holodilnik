import requests
from scrapy.http import HtmlResponse
from bhfutils.crawler.playwright.page import PageMethod


class HolodilnikDownloadMiddleware:
    def process_request(self, request, spider):
        if request.meta['spiderid'].endswith('HolodilnikProducts'):
            print('Mark playwright\n\n\n')
            request.meta['playwright'] = True
            request.meta['playwright_page_methods'] = [
                PageMethod('wait_for_selector', 'div#view-row')
            ]
        else:
            request.meta['playwright'] = False
