import os
import multiprocessing
import pickle
import sys
import helpers
import logging

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("startups.log")
formatter    = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def save_hiring_startup(startup_info):

    startup_name     = startup_info["name"]
    startup_url      = startup_info["url"]
    location         = startup_info["location"]
    hiring_file_name = "hiring_{}.pkl".format(location)
    pkl_dir_path     = os.path.join(os.getcwd(), "startups_info")
    hiring_file_path = os.path.join(pkl_dir_path, hiring_file_name)

    try:
        site_data = helpers.soupify_website(startup_url)
    except Exception as e:
        logger.error(e)
    else:
        # check if startup has a jobs page
        links = [link.get("href") for link in site_data.find_all("a")]

        has_jobs_page, jobs_page_url = helpers.startup_has_jobs_page(links)

        if has_jobs_page:
            jobs_page = helpers.handle_local_links(startup_url, jobs_page_url)
            startup_info["jobs_page"] = jobs_page

            logger.info("{} is hiring. More info at {}".format(
                startup_name,
                startup_info["jobs_page"]
            ))

            with open(hiring_file_path, "ab") as file:
                pickle.dump(startup_info, file)

        else:
            return False


def get_all_jobs_links(startup_info):
    jobs_page   = startup_info["jobs_page"]
    jobs_links  = helpers.extract_job_links(jobs_page)
    startup_info["job_listing_urls"] = jobs_links
    return startup_info


def get_startup_list_for_a_city(url):

    city            = helpers.extract_city_name(url)

    site_data       = helpers.soupify_website(url)

    links           = site_data.find_all("a", class_="main_link")
    invalid_domains = ["instagram", "twitter", "facebook", ".gov",
                       "diagrams", "play.google.com", "hulshare",
                       "bing", " ", "none", "angel", "linkedin",
                       "mylanderpages", "mtv", "null", "imdb", "pennygrabber",
                       "amazon", "youtube", "homedepot", "indiegogo",
                       "wordpress", "itunes"]
    startup_list    = []

    logger.info("Fetching startups in {}".format(city))

    for link in links:

        startup_url     = link.get("href").strip().lower()
        startup_name    = link.find("h1").text.strip().lower()

        if startup_url is None or startup_url == "":
            continue

        if any(domain in startup_url for domain in invalid_domains):
            continue

        startup_info    = {
            "name": startup_name,
            "url": helpers.remove_trailing_slash(startup_url),
            "location": city,
        }

        startup_list.append(startup_info)

    file_name       = helpers.set_file_name_to_city_name(city)
    file_path       = os.path.join(os.getcwd()+"/startups_info", file_name)

    with open(file_path, "wb") as startups_file:
        pickle.dump(startup_list, startups_file)


def get_all_cities():

    """
    Fetch all cities available on startups-list.com
    Append them to a list
    Save the list to a pickle object
    """

    site_data       = helpers.soupify_website("http://startups-list.com")
    cities_links    = site_data.find_all("a", class_="citylink")
    all_cities      = []

    for city_link in cities_links:

        city_name    = city_link.text.strip()

        if city_name == "Tel Aviv":
            continue

        all_cities.append(city_link.get("href"))

    with open("cities_urls.pkl", "wb") as cities_urls_output:
        pickle.dump(all_cities, cities_urls_output)


if __name__ == "__main__":

    sys.setrecursionlimit(1000)

    if not os.path.exists(os.path.join(os.getcwd(), "cities_urls.pkl")):
        get_all_cities()

    logger.info("Found cities_urls.pkl, proceeding to load the data ...")
    with open("cities_urls.pkl", "rb") as cities_urls_file:
        cities_urls = pickle.load(cities_urls_file)

    logger.info("Urls loaded !")

    if not helpers.directory_exists("startups_info", os.getcwd()):

        logger.info("Creating startups_info directory")
        os.mkdir(os.path.join(os.getcwd(), "startups_info"))
        logger.info("startups_info directory created")

        logger.info("Fetching startup list for all cities ...")
        with multiprocessing.Pool() as pool:
            result = pool.map(get_startup_list_for_a_city, cities_urls)

    logger.info("Found startup directory ... Loading filenames ...")
    startup_pkl_files = os.listdir(os.path.join(os.getcwd(), "startups_info"))
    startup_filenames   = [file for file in startup_pkl_files]

    logger.info("Checking startups for open jobs ...")
    for filename in startup_filenames:

        file_path = os.path.join(os.getcwd(), "startups_info", filename)

        with open(file_path, "rb") as startup_info_file:
            startup_list = pickle.load(startup_info_file)

        with multiprocessing.Pool() as pool:
            pool.map(save_hiring_startup, startup_list)

    logger.info("Done checking startups for open jobs")
    # for each hiring_startups file
    # in a multiprocessing pool
    # scrape every job page and get every link that satisfies the condition
    # ie do they match our list of keywords
    # startup_info["job_listing_urls"] = [link1, link2 etc]
