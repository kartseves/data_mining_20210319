import scrapy

from ..loaders import HhCompanyLoader, HhVacancyLoader
from ..spiders.xpaths import HH_PAGE_XPATH, HH_COMPANY_XPATH, HH_VACANCY_XPATH


class HhSpider(scrapy.Spider):
    name = "hh"
    allowed_domains = ["hh.ru"]
    start_urls = [
        "https://omsk.hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113"
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callbacks = {
            "pagination": self.parse,
            "company": self.company_parse,
            "vacancy": self.vacancy_parse,
        }
        self.coll_name = 'vacancy'

    @staticmethod
    def _get_follow_xpath(response, xpath, callback):
        for url in response.xpath(xpath):
            yield response.follow(url, callback=callback)

    def parse(self, response, *args, **kwargs):
        for key, xpath in HH_PAGE_XPATH.items():
            yield from self._get_follow_xpath(response, xpath, self.callbacks[key])

    def vacancy_parse(self, response):
        self.coll_name = "vacancy"
        loader = HhVacancyLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in HH_VACANCY_XPATH.items():
            loader.add_xpath(key, xpath)

        yield loader.load_item()

        yield from self._get_follow_xpath(response, HH_VACANCY_XPATH.get("author"), self.callbacks["company"])

    def company_parse(self, response):
        self.coll_name = "company"
        loader = HhCompanyLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in HH_COMPANY_XPATH.items():
            loader.add_xpath(key, xpath)

        yield loader.load_item()
