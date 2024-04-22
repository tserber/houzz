import json
from typing import Union

import requests
import toml
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


class PageData:

    def __init__(self, url_,
                 next_page_css_selector_=None,
                 business_class_=None,
                 init=False):

        self.url = url_
        self.domain = urlparse(self.url).netloc
        self.soup: Union[BeautifulSoup, None] = None
        self.next_page_css_selector = next_page_css_selector_
        self.business_class = business_class_
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
        a_element = self.soup.select_one(self.next_page_css_selector)
        assert a_element
        href = a_element['href']
        self.next_page_href = urljoin(self.domain, href)
        return self.next_page_href

    def get_businesses(self):
        self.businesses = self.soup.find_all("li", {"class": self.business_class})

    def parse_business(self, business_dict: dict):
        for b in self.businesses:  # simple parsing, better use id
            bdata = {'json': json.loads(b.script.text),
                     'all_data': b.text}
            bhref = b.a['href']
            if bhref in business_dict:
                # print(f'Business with link: {bhref}\nIs already added, skipping...')
                continue
            business_dict[bhref] = bdata


def write_to_json(file_path, data):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


if __name__ == '__main__':
    iter_pages = 10
    scrape_settings = toml.load('scrape_settings.toml')

    page = PageData(scrape_settings['url'], init=True)
    # TODO: calculate all possible pages and make asyncio pool to make multiple requests for each selection
    res_businesses = dict()
    for page_num in range(iter_pages-1):
        url = f"https://{page.domain}/{page.next_page_href}"
        # TODO: change businesses_class to css selector
        page = PageData(url,
                        scrape_settings['next_page_css_selector'],
                        scrape_settings['businesses_class'])
        page.get_page_bs()
        page.get_businesses()
        page.parse_business(res_businesses)

        next_page = page.get_next_page_href()
        print(f'scraped: {len(res_businesses)}')

    print(f'scraped: {len(res_businesses)}')

    write_to_json(file_path='data.json', data=res_businesses)
