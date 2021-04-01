import time
from urllib.parse import urljoin
import requests
import bs4
import datetime as dt

from sshtunnel import SSHTunnelForwarder
import pymongo


MONTHS = {
    "янв": 1,
    "фев": 2,
    "мар": 3,
    "апр": 4,
    "май": 5,
    "мая": 5,
    "июн": 6,
    "июл": 7,
    "авг": 8,
    "сен": 9,
    "окт": 10,
    "ноя": 11,
    "дек": 12,
}


def get_response(url, *args, **kwargs):
    for _ in range(10):
        response = requests.get(url, *args, **kwargs)
        if response.status_code == 200:
            return response
        time.sleep(1)
    raise ValueError("URL DIE")


class MagnitParse:
    def __init__(self, start_url, db_client):
        self.start_url = start_url
        self.db = db_client["gb_data_mining_20210319"]
        self.collection = self.db["magnit_products"]

    @staticmethod
    def get_soup(url) -> bs4.BeautifulSoup:
        return bs4.BeautifulSoup(get_response(url).text, "lxml")

    @property
    def template(self):
        data_template = {
            "url": lambda a: urljoin(self.start_url, a.attrs.get("href", "/")),
            "promo_name": lambda a: a.find("div", attrs={"class": "card-sale__header"}).text,
            "product_name": lambda a: a.find("div", attrs={"class": "card-sale__title"}).text,
            "old_price": lambda a: float(
                ".".join(
                    itm for itm in a.find("div", attrs={"class": "label__price_old"}).text.split()
                )
            ),
            "new_price": lambda a: float(
                ".".join(
                    itm for itm in a.find("div", attrs={"class": "label__price_new"}).text.split()
                )
            ),
            "image_url": lambda a: urljoin(
                self.start_url, a.find("picture").find("img").attrs.get("data-src", "")),
            "date_list": lambda a: self.__get_date(
                a.find("div", attrs={"class": "card-sale__date"}).text
            )
        }
        return data_template

    def run(self):
        for product in self._parse(self.get_soup(self.start_url)):
            self.save(product)

    def _parse(self, soup):
        product_a = soup.find_all('a', attrs={"class": "card-sale"})
        for prod_tag in product_a:
            product_data = {}
            for key, func in self.template.items():
                try:
                    product_data[key] = func(prod_tag)
                except (AttributeError, ValueError):
                    pass
            date_list = product_data.get("date_list")
            if date_list:
                product_data["date_from"] = date_list[0]
                product_data["date_to"] = date_list[1]
                product_data.pop("date_list")
            yield product_data

    def save(self, data: dict):
        self.collection.insert_one(data)

    @staticmethod
    def __get_date(date_string) -> list:
        date_list = date_string.replace("с ", "", 1).replace("\n", "").split("до")
        result = []
        for date in date_list:
            temp_date = date.split()
            result.append(
                dt.datetime(
                    year=dt.datetime.now().year,
                    day=int(temp_date[0]),
                    month=MONTHS[temp_date[1][:3]],
                )
            )
        return result


if __name__ == "__main__":
    mongo_server = SSHTunnelForwarder(
        "192.168.1.13",
        ssh_username="username",
        ssh_password="********",
        remote_bind_address=('127.0.0.1', 27017)
    )

    mongo_server.start()

    mongo_client = pymongo.MongoClient('127.0.0.1', mongo_server.local_bind_port)

    target_url = "https://magnit.ru/promo/"
    parser = MagnitParse(target_url, mongo_client)
    parser.run()

    mongo_server.stop()
