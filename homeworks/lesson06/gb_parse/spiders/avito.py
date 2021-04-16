import scrapy
import json
from urllib.parse import urljoin

from ..loaders import AvitoLoader
from ..spiders.xpaths import AVITO_FLAT_XPATH


class AvitoSpider(scrapy.Spider):
    name = "avito"
    allowed_domains = ["www.avito.ru"]
    start_urls = ["https://www.avito.ru/omsk/kvartiry/prodam"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coll_name = 'flat'
        self.page_num = 1
        self.flat_data = {}

    def _get_follow(self, response, callback):
        base_url = response.url.replace(f"?p={self.page_num}", '')
        self.page_num += 1
        yield response.follow(f"{base_url}?p={self.page_num}", callback=callback)

    def parse(self, response, *args, **kwargs):
        try:
            json_data = json.loads(response.xpath('//div[@class="js-initial"]/@data-state').extract_first())
            catalog = json_data.get('catalog', {})
            items = catalog.get('items')
            if items:
                yield response.follow(urljoin(response.url, catalog.get('pager').get('next')), self.parse)
                for item in items:
                    item_type = item.get('type')
                    if item_type == 'item':
                        # Здесь можно сохранить и передать в flat_parse какие-либо данные из словаря item
                        self.flat_data['price'] = item.get('priceDetailed').get('value')
                        yield response.follow(urljoin(response.url, item.get('urlPath')), self.flat_parse)
                    elif item_type == 'vip':
                        vip_items = item.get('items')
                        if vip_items:
                            for vip_item in vip_items:
                                # Здесь можно сохранить и передать в flat_parse какие-либо данные из словаря vip_item
                                self.flat_data['price'] = item.get('priceDetailed').get('value')
                                yield response.follow(urljoin(response.url, vip_item.get('urlPath')), self.flat_parse)
            else:
                yield self._get_follow(response, self.parse)
        except (ValueError, KeyError, AttributeError):
            yield self._get_follow(response, self.parse)

    def flat_parse(self, response):
        self.coll_name = "flat"
        loader = AvitoLoader(response=response)
        loader.add_value("url", response.url)

        # Доабвляем данные, которые собрали на родительской странице
        for key, value in self.flat_data.items():
            loader.add_value(key, value)

        for key, xpath in AVITO_FLAT_XPATH.items():
            loader.add_xpath(key, xpath)

        yield loader.load_item()
