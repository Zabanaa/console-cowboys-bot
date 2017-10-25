import os, logging, multiprocessing, requests, pickle
from bs4 import BeautifulSoup

# Scrape All Lists for every city
# save that into a pickle
# then at runtime do an if check on the presence of a pickle file
# For every city, visit every site and check that they have a jobs section

def get_startups_list_for_a_city(url):
    site_data = soupify_website(url)
    print(site_data)
    return site_data

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

# 1. Scrape the list of cities and add them to a pickle object

def soupify_website(site_url):
    sauce = requests.get(site_url, timeout=20).text
    return BeautifulSoup(sauce, "html.parser")

# def get_startups_list(city):

#     ## go and fetch the list at city.startups-list.com
#     ## once there turn that into a soup
#     site_url = "{}.startups-list.com".format(city)
#     soup = soupify_website(site_url)
#     # save the list of links to its own pickle file
#     pass

def handle_local_links(url, link):
    # if link is local, prepend the url, else return the link as is
    pass

## for each pickle file (aka each city)
## go ahead and visit every site and get the data

if __name__ == "__main__":

    if not os.path.exists(os.path.join(os.getcwd(), "cities_urls.pkl")):
        get_all_cities()

    with open("cities_urls.pkl", "rb") as cities_urls_file:
        cities_urls = pickle.load(cities_urls_file)

## // Do this in a multiprocessing pool
## For each city in the list
## Go and Grab the list of startups

## // Do this in a multiprocessing pool
## put em in their own pickle file
## for each pickle file
    ## visit every site and check if they have career pages
    ## if they do, find the job link and add it to the mongo DB
