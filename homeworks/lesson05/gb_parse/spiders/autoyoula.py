import scrapy

from ..loaders import AutoyoulaLoader
from ..spiders.xpaths import AUTO_YOULA_PAGE_XPATH, AUTO_YOULA_BRAND_XPATH, AUTO_YOULA_CAR_XPATH


class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callbacks = {
            "pagination": self.parse,
            "brands": self.brand_parse,
            "car": self.car_parse
        }

    @staticmethod
    def _get_follow_xpath(response, xpath, callback):
        for link in response.xpath(xpath):
            yield response.follow(link, callback=callback)

    def parse(self, response, *args, **kwargs):
        for key, xpath in AUTO_YOULA_PAGE_XPATH.items():
            yield from self._get_follow_xpath(response, xpath, self.callbacks[key])

    def brand_parse(self, response, *args, **kwargs):
        for key, xpath in AUTO_YOULA_BRAND_XPATH.items():
            yield from self._get_follow_xpath(response, xpath, self.callbacks[key])

    def car_parse(self, response):
        loader = AutoyoulaLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in AUTO_YOULA_CAR_XPATH.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
