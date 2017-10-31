from urllib.parse import urlparse
from app import logger
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


def startup_has_jobs_page(links):

    keywords = ["careers", "jobs", "join-us",
                "work-for-us", "work-with-us",
                "join-the-team", "hiring"]

    for link in links:

        if link is not None and any(keyword in link for keyword in keywords):
            return True, link
        else:
            continue
    else:
        return False, None


def set_file_name_to_city_name(city_name):
    file_name = "{}.pkl".format(city_name)
    return file_name


def soupify_website(site_url):
    try:
        sauce = requests.get(site_url, timeout=5).text
    except requests.exceptions.RequestException as e:
        raise Exception("Couldn't load {}".format(site_url))
    else:
        return BeautifulSoup(sauce, "html.parser")


def handle_local_links(url, link):
    # if link is local, prepend the url, else return the link as is
    pattern = re.compile(r"https?://[a-zA-Z0-9-.]*\.[a-zA-Z]+")
    main_url     = pattern.findall(url)[0]

    if link.startswith("/"):
        link = main_url + link

    if not link.startswith("/") and not link.startswith("http"):
        link = main_url + "/" + link
    return link


def remove_trailing_slash(url):
    clean_url   = re.sub("\/$", "", url)
    return clean_url


def directory_exists(dir_name, path):
    return os.path.isdir(os.path.join(path, dir_name))


def extract_jobs(url):

    site_data = soupify_website(url)
    keywords  = ["python", "nodejs", "node.js", "django", "flask",
                 "full stack", "fullstack", "full stack", "backend",
                 "back end", "back-end", "software developer",
                 "software engineer", "rust", "ruby", "golang", "c++",
                 "devops", "swift", "android", "kotlin", "scala", "java",
                 "php", "laravel", "web engineer", "engineering manager", "ios"
                 "it specialist", "api developer", "api engineer"]

    jobs = []

    for link in site_data.find_all("a"):
        if link.text is not None and any(
            keyword in link.text.lower() for keyword in keywords
        ):
            job_link = handle_local_links(url, link.get("href"))
            jobs.append({
                "title": link.text,
                "url": job_link,
            })

    return jobs
