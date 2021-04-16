import re
from urllib.parse import urljoin

from scrapy.loader import ItemLoader
from scrapy import Selector
from itemloaders.processors import TakeFirst, MapCompose


def clear_price(price: str) -> float:
    try:
        result = float(price.replace("\u2009", ""))
    except ValueError:
        result = None
    return result


def get_specs(item: str) -> dict:
    selector = Selector(text=item)
    data = {
        "name": selector.xpath("//div[contains(@class, 'AdvertSpecs')]/text()").extract_first(),
        "value": selector.xpath(
            "//div[contains(@class, 'AdvertSpecs_data')]//text()"
        ).extract_first(),
    }
    return data


def get_seller_id(text):
    re_pattern = re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar")
    result = re.findall(re_pattern, text)
    try:
        user_link = f"https://youla.ru/user/{result[0]}"
    except IndexError:
        user_link = ""
    return user_link


def flat_text(items):
    return "\n".join(items)


def hh_user_url(user_id):
    return urljoin("https://hh.ru/", user_id)


def hh_company_name(items):
    return "".join(items).replace("\xa0", " ")[:-1]


def hh_company_desc(items):
    return "".join(items).replace("\xa0", " ")


def get_params(item: str) -> dict:
    selector = Selector(text=item)
    data = {
        "name": selector.xpath('//span[@class="item-params-label"]/text()').extract_first(),
        "value": selector.xpath('//li/text()').extract()[1].replace("\xa0", " "),
    }
    return data


class AutoyoulaLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_in = MapCompose(clear_price)
    price_out = TakeFirst()
    specs_in = MapCompose(get_specs)
    description_out = TakeFirst()
    seller_in = MapCompose(get_seller_id)
    seller_out = TakeFirst()


class HhCompanyLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    company_site_out = TakeFirst()
    company_name_out = hh_company_name
    company_desc_out = hh_company_desc


class HhVacancyLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_out = flat_text
    author_in = MapCompose(hh_user_url)
    author_out = TakeFirst()


class AvitoLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_out = TakeFirst()
    address_out = TakeFirst()
    params_in = MapCompose(get_params)
