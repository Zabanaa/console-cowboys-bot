from urllib.parse import urlparse
import re
import os
import logging
import sys

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def extract_city_name(url):
    """
    Extracts the city name from the given url.
    Example: boston.startups-list.com should return boston.
    There are cases where the urls don't follow the pattern of
    location.startups-list.com, they are also handled.
    """
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

    """
    Given a list of links, this function compares each link against a list of
    relevant keywords and returns a tuple (True, link) if a match is found and
    (false, None) if there isn't any.
    """

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
    """
    Accepts the city_name as the argument and apppends a .pkl extension to it.
    returns the filename
    """
    file_name = "{}.pkl".format(city_name)
    return file_name


def soupify_website(site_url):
    """
    Makes an HTTP request to the site_url.
    Passes the response to a BeautifulSoup object that is then returned.
    """
    try:
        sauce = requests.get(site_url, timeout=5).text
    except requests.exceptions.RequestException as e:
        raise Exception("Couldn't load {}".format(site_url))
        logger.error("Couldn't load {}".format(site_url))
    else:
        return BeautifulSoup(sauce, "html.parser")


def handle_local_links(url, link):

    """
    This helper function will append any relative link to its absolute url.
    Example: if the link is "/jobs/apply" and then url is "http://google.com/"
    It merges the two to create a new url: "http://google.com/jobs/apply".
    Returns the link.
    """
    pattern         = re.compile(r"https?://[a-zA-Z0-9-.]*\.[a-zA-Z]+")
    main_url        = pattern.findall(url)[0]

    if link.startswith("/"):
        link = main_url + link

    if not link.startswith("/") and not link.startswith("http"):
        link = main_url + "/" + link
    return link


def remove_trailing_slash(url):
    """
    Removes trailing slash from a URL and returns it.
    """
    clean_url   = re.sub("\/$", "", url)
    return clean_url


def extract_software_job_links(url):

    """
    Tests all links in a jobs page and tests them against a list of relevant
    Keywords and expressions. If a match is found, the href and innerHTML (text)
    attribute are extracted in a dictionary which itself is appended to the jobs
    list that is eventually returned.
    """

    keywords  = ["python", "nodejs", "node.js", "django", "flask",
                 "full stack", "fullstack", "full stack", "backend",
                 "back end", "back-end", "software developer",
                 "software engineer", "rust", "ruby", "golang", "c++",
                 "devops", "swift", "android", "kotlin", "scala", "java",
                 "php", "laravel", "web engineer", "engineering manager", "ios"
                 "it specialist", "api developer", "api engineer"]

    jobs = []

    try:
        site_data = soupify_website(url)
    except Exception as e:
        logger.error("{} is unreachable".format(url))
    else:
        for link in site_data.find_all("a"):
            if link.text is not None and any(
                keyword in link.text.lower() for keyword in keywords
            ):

                if link.get("href") is not None:
                    job_link = handle_local_links(url, link.get("href"))

                    jobs.append({
                        "title": link.text.strip(),
                        "url": job_link,
                    })
                else:
                    continue
            else:
                continue

    return jobs
