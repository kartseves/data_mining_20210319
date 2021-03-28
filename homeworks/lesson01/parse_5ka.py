# Задача 1
#
# Источник: https://5ka.ru/special_offers/
#
# Задача организовать сбор данных, необходимо иметь метод сохранения данных в .json файлы.
# Результат: Данные скачиваются с источника, при вызове метода/функции сохранения в файл.
# Скачанные данные сохраняются в Json файлы, для каждой категории товаров должен быть создан
# отдельный файл и содержать товары исключительно соответсвующие данной категории.
#
# Пример структуры данных для файла: нейминг ключей можно делать отличным от примера
#
# {
#     "name": "имя категории",
#     "code": "Код соответсвующий категории (используется в запросах)",
#     "products": [{PRODUCT}, {PRODUCT}........]  # список словарей товаров соответсвующих данной категории
# }


import time
import json
from pathlib import Path
import requests


class ParseProduct:
    headers = {"User-Agent": "YaBrowser/21.2.4.172"}

    def __init__(self, start_url: str, root_path: Path):
        self.start_url = start_url
        self.root_path = root_path

    def _get_response(self, curr_url):
        while True:
            response = requests.get(curr_url, headers=self.headers)
            if response.status_code == 200:
                return response
            time.sleep(0.5)

    def run(self):
        for product in self._parse(self.start_url):
            product_path = self.root_path.joinpath(f"{product['id']}.json")
            self._save(product, product_path)

    def _parse(self, curr_url: str):
        while curr_url:
            response = self._get_response(curr_url)
            data: dict = response.json()
            curr_url = data["next"]
            for product in data["results"]:
                yield product

    def _save(self, data: dict, file_path: Path):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)


class ParseCat(ParseProduct):
    def __init__(self, target_url, *args, **kwargs):
        self.target_url = target_url
        super().__init__(*args, **kwargs)

    def _get_cat(self):
        response = self._get_response(self.target_url)
        data = response.json()
        return data

    def run(self):
        for curr_cat in self._get_cat():
            result_cat = {"name": curr_cat['parent_group_name'],
                          "code": curr_cat['parent_group_code'],
                          "products": []}

            curr_params = f"?categories={curr_cat['parent_group_code']}"
            curr_url = f"{self.start_url}{curr_params}"

            result_cat["products"].extend(list(self._parse(curr_url)))
            file_name = f"{curr_cat['parent_group_code']}_{curr_cat['parent_group_name']}.json"
            cat_path = self.root_path.joinpath(file_name)
            self._save(result_cat, cat_path)


def get_save_path(dir_name):
    curr_save_path = Path(__file__).parent.joinpath(dir_name)
    if not curr_save_path.exists():
        curr_save_path.mkdir()
    return curr_save_path


if __name__ == "__main__":
    product_url = "https://5ka.ru/api/v2/special_offers/"
    cat_url = "https://5ka.ru/api/v2/categories/"

    save_path = get_save_path("product_by_cat")
    cat_parser = ParseCat(cat_url, product_url, save_path)
    cat_parser.run()
