from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

def extract_city_name(url):
    full_url = urlparse(url)
    city_name = full_url.hostname.split(".")[0]
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

def cleanup_startup_url(url):
    # find the traling slash and remove it
    pass
