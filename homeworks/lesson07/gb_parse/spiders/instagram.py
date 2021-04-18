import scrapy
import json
import datetime as dt
from urllib.parse import urlencode, urljoin

from ..items import InstaTag, InstaPost


class InstagramSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["www.instagram.com"]
    start_urls = ["https://www.instagram.com/"]
    _login_url = "https://www.instagram.com/accounts/login/ajax/"
    _tags_url = "/explore/tags/"
    api_url = "/graphql/query/"
    coll_name = ""

    def __init__(self, login, enc_password, tags, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.enc_password = enc_password
        self.tags = tags

    @staticmethod
    def json_data_extract(response):
        json_text = response.xpath(
            "//script[contains(text(), 'window._sharedData = ')]/text()"
        ).extract_first()
        return json.loads(json_text.replace("window._sharedData = ", "")[:-1])

    def parse(self, response, *args, **kwargs):
        try:
            json_data = self.json_data_extract(response)
            yield scrapy.FormRequest(
                self._login_url,
                method="POST",
                callback=self.parse,
                formdata={"username": self.login, "enc_password": self.enc_password},
                headers={"X-CSRFToken": json_data["config"]["csrf_token"]},
            )
        except AttributeError as e:
            print(e)
            if response.json()["authenticated"]:
                for tag in self.tags:
                    yield response.follow(f"{self._tags_url}{tag}/", callback=self.tag_page_parse)

    def tag_page_parse(self, response):
        json_data = self.json_data_extract(response)
        insta_tag = InstTag(json_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"])
        self.coll_name = "tags"
        yield insta_tag.get_tag_item()
        self.coll_name = "posts"
        yield from insta_tag.get_post_items()
        yield response.follow(
            f"{self.api_url}?{urlencode(insta_tag.paginate_params())}",
            callback=self._api_tag_parse,
        )

    def _api_tag_parse(self, response):
        json_data = response.json()
        insta_tag = InstTag(json_data["data"]["hashtag"])
        self.coll_name = "posts"
        yield from insta_tag.get_post_items()
        yield response.follow(
            f"{self.api_url}?{urlencode(insta_tag.paginate_params())}",
            callback=self._api_tag_parse,
        )


class InstTag:
    query_hash = "9b498c08113f1e09617a1703c22b2f32"

    def __init__(self, hashtag: dict):
        self.variables = {
            "tag_name": hashtag["name"],
            "first": 100,
            "after": hashtag["edge_hashtag_to_media"]["page_info"]["end_cursor"],
        }
        self.hashtag = hashtag

    def paginate_params(self):
        url_query = {"query_hash": self.query_hash, "variables": json.dumps(self.variables)}
        return url_query

    def get_tag_item(self):
        data = {}
        for key, value in self.hashtag.items():
            if not (isinstance(value, dict) or isinstance(value, list)):
                data[key] = value
        return InstaTag(date_parse=dt.datetime.utcnow(), data=data)

    def get_post_items(self):
        for edge in self.hashtag["edge_hashtag_to_media"]["edges"]:
            yield InstaPost(date_parse=dt.datetime.utcnow(), data=edge["node"], photos=[edge["node"]["display_url"]])
