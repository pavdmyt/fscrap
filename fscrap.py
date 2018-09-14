# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime

import requests
import simplejson as json
from lxml import html


# TODO: add logging


_PY_VER = sys.version_info
if _PY_VER < (3, 6):
    raise RuntimeError("fscrap requires Python verion >= 3.6")


URL = "http://127.0.0.1:8000/"
QTY = 10  # how many elements to scrap
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
DUMP_FNAME = "post_data.json"

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
    # Srap the page
    page = requests.get(URL)
    tree = html.fromstring(page.content)

    titles = get_elements(tree, POST_TITLE_TMPL, qty=QTY)
    dates = get_elements(tree, POST_DATE_TMPL, qty=QTY)

    # Build JSON
    parsed_data = {}
    for title, date in zip(titles, dates):
        date_dict = parse_date(date)
        post_data = {**parse_title(title), **date_dict}
        date_str = f'{date_dict["day"]} {date_dict["time"]}'
        key = datetime_to_epoch(date_str)
        parsed_data[int(key)] = post_data

    #
    # Write JSON to FS
    #

    # Load data

    # XXX: Maybe it is better to store this data in .cache ?
    fpath = os.path.join(THIS_DIR, DUMP_FNAME)
    if os.path.exists(fpath):
        with open(fpath, "r") as fp:
            existing_data = json.load(fp)
    else:
        existing_data = {}

    # Merge and write data
    new_data = {**existing_data, **parsed_data}
    with open(fpath, "w") as fp:
        json.dump(new_data, fp)

    print(f"* Saved to {fpath}")


if __name__ == "__main__":
    main()
