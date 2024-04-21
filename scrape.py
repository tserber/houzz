import json
from typing import Union

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


class PageData:

    def __init__(self, url_, init=False):
        self.url = url_
        self.domain = urlparse(self.url).netloc
        self.soup: Union[BeautifulSoup, None] = None
        self.page = None
        self.next_page_href = None
        self.businesses: Union[list, None] = None

        if init:
            self.domain = urlparse(self.url).netloc
            self.next_page_href = self.url.split(self.domain)[-1][1:]

    def get_page_bs(self):
        print(f'Opening url: {url}')
        self.page = requests.get(self.url)
        if not self.page.status_code == 200:
            raise ConnectionError
        self.soup = BeautifulSoup(self.page.text, 'html.parser')
        return self.soup

    def get_next_page_href(self):
        a_element = self.soup.select_one(next_page_css_selector)
        assert a_element
        href = a_element['href']
        self.next_page_href = urljoin(self.domain, href)
        return self.next_page_href

    def get_businesses(self):
        self.businesses = self.soup.find_all("li", {"class": "hz-pro-search-results__item"})

    def parse_business(self, business_dict: dict):
        for b in self.businesses:  # simple parsing, better use id
            bdata = {'json': json.loads(b.script.text),
                     'all_data': b.text}
            bhref = b.a['href']
            if bhref in business_dict:
                # print(f'Business with link: {bhref}\nIs already added, skipping...')
                continue
            business_dict[bhref] = bdata


if __name__ == '__main__':
    iter_pages = 10
    url = 'https://www.houzz.com/professionals/general-contractor/brentwood-los-angeles-ca-us-probr0-bo~t_11786~r_101182514'
    next_page_css_selector = 'a.hz-pagination-link--next'
    businesses_class = 'hz-pro-search-results__item'
    page = PageData(url, init=True)
    # TODO: calculate all possible pages and make asyncio pool to make multiple requests for each selection
    res_businesses = dict()
    for page_num in range(iter_pages-1):
        url = f"https://{page.domain}/{page.next_page_href}"
        page = PageData(url)
        page.get_page_bs()
        page.get_businesses()
        page.parse_business(res_businesses)

        next_page = page.get_next_page_href()
        print(f'scraped: {len(res_businesses)}')

    print(f'scraped: {len(res_businesses)}')
