# -*- coding: utf-8 -*-

import sys
from datetime import datetime
from pprint import pprint

import requests
from lxml import html


_PY_VER = sys.version_info
if _PY_VER < (3, 6):
    raise RuntimeError("fscrap requires Python verion >= 3.6")


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


def datetime_to_epoch(time_str, fmt="%d-%m-%Y %H:%M"):
    d = datetime.strptime(time_str, fmt)
    return d.strftime("%s")


def main():
    page = requests.get(URL)
    tree = html.fromstring(page.content)

    titles = get_elements(tree, POST_TITLE_TMPL, qty=QTY)
    dates = get_elements(tree, POST_DATE_TMPL, qty=QTY)

    res = {}
    for title, date in zip(titles, dates):
        date_dict = parse_date(date)
        post_data = {**parse_title(title), **date_dict}
        date_str = f'{date_dict["day"]} {date_dict["time"]}'
        key = datetime_to_epoch(date_str)
        res[int(key)] = post_data

    pprint(res)


if __name__ == "__main__":
    main()
