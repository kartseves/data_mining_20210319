import re
import scrapy

from sshtunnel import SSHTunnelForwarder
from pymongo import MongoClient


class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]

    @staticmethod
    def get_author_id(response):
        marker = "window.transitState = decodeURIComponent"
        for script in response.css("script"):
            try:
                if marker in script.css("::text").extract_first():
                    re_pattern = re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar")
                    result = re.findall(re_pattern, script.css("::text").extract_first())
                    return (
                        response.urljoin(f"/user/{result[0]}").replace("auto.", "", 1)
                        if result
                        else None
                    )
            except TypeError:
                pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = MongoClient()
        mongo_server = SSHTunnelForwarder(
            "192.168.1.13",
            ssh_username="username",
            ssh_password="********",
            remote_bind_address=('127.0.0.1', 27017)
        )
        mongo_server.start()
        self.mongo_server = mongo_server
        mongo_client = MongoClient('127.0.0.1', mongo_server.local_bind_port)
        self.db = mongo_client["gb_data_mining_20210319"]

    def __del__(self):
        self.mongo_server.stop()

    def _get_follow(self, response, select_str, callback, **kwargs):
        for a in response.css(select_str):
            url = a.attrib.get("href")
            yield response.follow(url, callback=callback, **kwargs)

    def parse(self, response, **kwargs):
        yield from self._get_follow(
            response, "div.TransportMainFilters_brandsList__2tIkv a.blackLink", self.brand_parse
        )

    def brand_parse(self, response):
        yield from self._get_follow(
            response, "div.Paginator_block__2XAPy a.Paginator_button__u1e7D", self.brand_parse
        )
        yield from self._get_follow(
            response,
            "article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu",
            self.car_parse,
        )

    def car_parse(self, response):
        try:
            data = {
                "seller": AutoyoulaSpider.get_author_id(response),
                "url": response.url,
                "title": response.css("div.AdvertCard_advertTitle__1S1Ak::text").extract_first(),
                "price": float(
                    response.css("div.AdvertCard_price__3dDCr::text").extract_first().replace("\u2009", "")
                ),
                "photos_url": response.css("img.PhotoGallery_photoImage__2mHGn::attr(src)").extract(),
                "specs": [],
                "description": response.css("div.AdvertCard_descriptionInner__KnuRi::text").extract_first()
            }

            for items in response.css("div.AdvertSpecs_row__ljPcX"):
                div_data = items.css("div.AdvertSpecs_data__xK2Qx::text").extract_first()
                data["specs"].append(
                    {"name": items.css("div.AdvertSpecs_label__2JHnS::text").extract_first(),
                     "value": div_data if div_data else items.css("div.AdvertSpecs_data__xK2Qx a::text").extract_first()
                     }
                )

            self.db[self.name].insert_one(data)

        except (ValueError, AttributeError):
            pass
