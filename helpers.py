from urllib.parse import urlparse
import re
import os

import requests
from bs4 import BeautifulSoup


def extract_city_name(url):
    full_url = urlparse(url)
    city_name = full_url.hostname.split(".")[0]

    if "nyc" in city_name:
        city_name = "new-york"
    elif "mtl" in city_name:
        city_name = "montreal"
    elif "startupsla" in city_name:
        city_name = "los-angeles"
    elif "boston" in city_name:
        city_name = "boston"
    elif "chicago" in city_name:
        city_name = "chicago"
    elif "boulder" in city_name:
        city_name = "boulder"

    return city_name


def set_file_name_to_city_name(city_name):
    file_name = "{}.pkl".format(city_name)
    return file_name


def soupify_website(site_url):
    sauce = requests.get(site_url, timeout=20).text
    return BeautifulSoup(sauce, "html.parser")


def handle_local_links(url, link):
    # if link is local, prepend the url, else return the link as is
    pass


def remove_trailing_slash(url):
    clean_url   = re.sub("\/$", "", url)
    return clean_url


def directory_exists(dir_name, path):
    return os.path.isdir(os.path.join(path, dir_name))
