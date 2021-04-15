import scrapy

from ..loaders import AvitoLoader
from ..spiders.xpaths import AVITO_PAGE_XPATH, AVITO_FLAT_XPATH


class AvitoSpider(scrapy.Spider):
    name = "avito"
    allowed_domains = ["www.avito.ru"]
    start_urls = ["https://www.avito.ru/omsk/kvartiry/prodam/"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callbacks = {
            "pagination": self.parse,
            "flat": self.flat_parse,
        }
        self.coll_name = 'flat'

    @staticmethod
    def _get_follow_xpath(response, xpath, callback):
        for link in response.xpath(xpath):
            yield response.follow(link, callback=callback)

    def parse(self, response, *args, **kwargs):
        for key, xpath in AVITO_PAGE_XPATH.items():
            yield from self._get_follow_xpath(response, xpath, self.callbacks[key])

    def flat_parse(self, response):
        self.coll_name = "flat"
        loader = AvitoLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in AVITO_FLAT_XPATH.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
