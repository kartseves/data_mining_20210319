AUTO_YOULA_PAGE_XPATH = {
    "brands": '//div[@data-target="transport-main-filters"]/'
              'div[contains(@class, "TransportMainFilters_brandsList")]//'
              'a[@data-target="brand"]/@href',
}

AUTO_YOULA_BRAND_XPATH = {
    "pagination": '//a[@data-target-id="button-link-serp-paginator"]/@href',
    "car": '//article[@data-target="serp-snippet"]//a[@data-target="serp-snippet-title"]/@href',
}

AUTO_YOULA_CAR_XPATH = {
    "seller": '//body/script[contains(text(), "window.transitState = decodeURIComponent")]'
              '/text()',
    "title": '//div[@data-target="advert-title"]/text()',
    "price": '//div[@data-target="advert-price"]/text()',
    "photos_url": '//div[contains(@class, "PhotoGallery_photoWrapper")]/figure//img/@src',
    "specs": '//div[contains(@class, "AdvertCard_specs")]'
             '//div[contains(@class, "AdvertSpecs_row")]',
    "descriptions": '//div[@data-target="advert-info-descriptionFull"]/text()',
}

HH_PAGE_XPATH = {
    "pagination": '//div[@data-qa="pager-block"]//a[@data-qa="pager-page"]/@href',
    "vacancy": '//div[contains(@data-qa, "vacancy-serp__vacancy")]//'
    'a[@data-qa="vacancy-serp__vacancy-title"]/@href',
}

HH_COMPANY_XPATH = {
    "company_name": '//div[@class="employer-sidebar-header"]//'
                    'span[@data-qa="company-header-title-name"]/text()',
    "company_site": '//div[@class="employer-sidebar"]/'
                    'div[@class="employer-sidebar-content"]//'
                    'a[@data-qa="sidebar-company-site"]/@href',
    "field_of_activity": '//div[@class="employer-sidebar"]/'
                         'div[@class="employer-sidebar-content"]//p/text()',
    "company_desc": '//div[@data-qa="company-description-text"]//text()',
}

HH_VACANCY_XPATH = {
    "title": '//h1[@data-qa="vacancy-title"]/text()',
    "salary": '//p[@class="vacancy-salary"]/span/text()',
    "description": '//div[@data-qa="vacancy-description"]//text()',
    "skills": '//div[@class="bloko-tag-list"]//'
              'div[contains(@data-qa, "skills-element")]/'
              'span[@data-qa="bloko-tag__text"]/text()',
    "author": '//a[@data-qa="vacancy-company-name"]/@href',
}

AVITO_FLAT_XPATH = {
    "title": '//h1[@class="title-info-title"]/span/text()',
    "address": '//div[@class="item-address"]/span[@class="item-address__string"]/text()',
    "params": '//div[@class="item-params"]//ul[@class="item-params-list"]//li[@class="item-params-list-item"]',
}
