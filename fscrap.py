# -*- coding: utf-8 -*-

import sys
from pprint import pprint

import requests
from lxml import html


_PY_VER = sys.version_info
if _PY_VER < (3, 5):
    raise RuntimeError("fscrap requires Python verion >= 3.5")


URL = "http://127.0.0.1:8000/"
QTY = 10  # how many elements to scrap

# XPath selectors
POST_TITLE_TMPL = '//*[@id="dle-content"]/div[{0}]/div[1]/a'
POST_DATE_TMPL = '//*[@id="dle-content"]/div[{0}]/div[2]/span[1]'


def get_elements(page_tree, xpath_tmpl, qty=0):
    elements = []
    for elem_num in range(1, qty + 1):
        elem_xpath = xpath_tmpl.format(elem_num)
        element = page_tree.xpath(elem_xpath)
        elements.append(element[0])

    return elements


def parse_title(title_element):
    def sanitize_title(title):
        return title.strip(" \xa02")

    text = title_element.text
    title = sanitize_title(text) if text else ""
    url = title_element.values()[0]
    return {"title": title, "url": url}


def parse_date(date_element):
    text = date_element.text
    day, time = text.split(", ")
    return {"day": day, "time": time}


def main():
    page = requests.get(URL)
    tree = html.fromstring(page.content)

    titles = get_elements(tree, POST_TITLE_TMPL, qty=QTY)
    dates = get_elements(tree, POST_DATE_TMPL, qty=QTY)
    for title, date in zip(titles, dates):
        post_data = {**parse_title(title), **parse_date(date)}
        pprint(post_data)


if __name__ == "__main__":
    main()
