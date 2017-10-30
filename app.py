import os
import multiprocessing
import pickle
import sys
import helpers


from termcolor import colored

def check_startup_for_open_jobs(startup_info):

    startup_name     = startup_info["name"]
    startup_url      = startup_info["url"]
    location         = startup_info["location"]
    hiring_file_name = "hiring_{}.pkl".format(location)
    pkl_dir_path     = os.path.join(os.getcwd(), "startups_info")
    hiring_file_path = os.path.join(pkl_dir_path, hiring_file_name)

    try:
        site_data = helpers.soupify_website(startup_url)
    except Exception as e:
        print(colored(e, "red"))
    else:
        # check if startup has a jobs page
        print("{} - {}".format(startup_name, location))
        links = [link.get("href") for link in site_data.find_all("a")]

        has_jobs_page, jobs_page_url = helpers.startup_has_jobs_page(links)

        if has_jobs_page:
            jobs_page = helpers.handle_local_links(startup_url, jobs_page_url)
            startup_info["jobs_page"] = jobs_page

            print(colored("{} is hiring. More info at {}".format(
                startup_name,
                startup_info["jobs_page"]
            ), "green"))

            with open(hiring_file_path, "wb") as file:
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

    print("Getting data for {}".format(city))

    site_data       = helpers.soupify_website(url)
    links           = site_data.find_all("a", class_="main_link")
    invalid_domains = ["instagram", "twitter", "facebook", ".gov",
                       "diagrams", "play.google.com", "hulshare",
                       "bing", " ", "none", "angel", "linkedin",
                       "mylanderpages", "mtv", "null", "imdb", "pennygrabber",
                       "amazon", "youtube", "homedepot", "indiegogo",
                       "wordpress", "itunes"]
    startup_list    = []

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

    print("Done fetching data for {}".format(city))


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

    print("Found cities_urls.pkl, proceeding to load the data ...")
    with open("cities_urls.pkl", "rb") as cities_urls_file:
        cities_urls = pickle.load(cities_urls_file)

    print("Urls loaded !")

    if not helpers.directory_exists("startups_info", os.getcwd()):

        print("Creating startups_info directory")
        os.mkdir(os.path.join(os.getcwd(), "startups_info"))
        print("startups_info directory created")

        with multiprocessing.Pool() as pool:
            print("Fetching startup list for all cities ...")
            result = pool.map(get_startup_list_for_a_city, cities_urls)

        print("Done !")

    print("Found startup directory ... Loading filenames ...")
    startup_pkl_files = os.listdir(os.path.join(os.getcwd(), "startups_info"))
    startup_filenames   = [file for file in startup_pkl_files]

    for filename in startup_filenames:

        file_path = os.path.join(os.getcwd(), "startups_info", filename)

        with open(file_path, "rb") as startup_info_file:
            startup_list = pickle.load(startup_info_file)

        with multiprocessing.Pool() as pool:
            pool.map(check_startup_for_open_jobs, startup_list)

    # for each hiring_startups file
        # in a multiprocessing pool
        # scrape every job page and get every link that satisfies the condition
        # ie do they match our list of keywords
        # startup_info["job_listing_urls"] = [link1, link2 etc]

    print("Done!")
    # scrape_startup_site({"name": "ginger.io",
    #                      "location": "sf",
    #                      "url": "https://ginger.io"})
