from urllib.parse import urlparse
import os, logging, multiprocessing, requests, pickle, sys, random
from bs4 import BeautifulSoup
from helpers import soupify_website, extract_city_name

# Scrape All Lists for every city
# save that into a pickle
# then at runtime do an if check on the presence of a pickle file
# For every city, visit every site and check that they have a jobs section

def get_startup_list_for_a_city(url):
    site_data       = soupify_website(url)
    links           = site_data.find_all("a", class_="main_link")
    startup_list    = []

    for link in links:

        startup_url = link.get("href")
        startup_name = link.find("h1").text

        startup_info = {
            "name": startup_name.strip(),
            "url": startup_url.strip(),
        }

        startup_list.append(startup_info)

    file_name       = extract_city_name(url)

    with open(file_name, "wb") as startups_file:
        pickle.dump(startup_list, startups_file)

def get_all_cities():

    """
    Fetch all cities available on startups-list.com
    Append them to a list
    Save the list to a pickle object
    """

    site_data = soupify_website("http://startups-list.com")
    cities_links = site_data.find_all("a", class_="citylink")

    all_cities = []

    for city_link in cities_links:

        city_name = city_link.text.strip()

        if city_name == "Tel Aviv":
            continue

        all_cities.append(city_link.get("href"))

    with open("cities_urls.pkl", "wb") as cities_urls_output:
        pickle.dump(all_cities, cities_urls_output)

def handle_local_links(url, link):
    # if link is local, prepend the url, else return the link as is
    pass

## for each pickle file (aka each city)
## go ahead and visit every site and get the data

if __name__ == "__main__":

    sys.setrecursionlimit(1000)

    if not os.path.exists(os.path.join(os.getcwd(), "cities_urls.pkl")):
        get_all_cities()

    print("Found cities_urls.pkl, proceeding to load the data ...")
    with open("cities_urls.pkl", "rb") as cities_urls_file:
        cities_urls = pickle.load(cities_urls_file)

    print("Urls loaded !")

    with multiprocessing.Pool() as pool:
        print("Getting info for atlanta")
        result = pool.map(get_startup_list_for_a_city, ["http://atlanta.startups-list.com"])


## // Do this in a multiprocessing pool
## For each city in the list
## Go and Grab the list of startups

## // Do this in a multiprocessing pool
## put em in their own pickle file
## for each pickle file
    ## visit every site and check if they have career pages
    ## if they do, find the job link and add it to the mongo DB
