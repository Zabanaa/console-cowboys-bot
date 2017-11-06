import os
import multiprocessing
import pickle
import sys
import helpers
import logging
from db import JobsDB

logging.basicConfig(
                level=logging.INFO,
                filename="startups.log",
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
logger          = logging.getLogger("main")

CWD = os.getcwd()
STARTUPS_INFO_DIR   = os.path.join(CWD, "startups_info")
HIRING_STARTUPS_DIR = os.path.join(CWD, "hiring_startups")
CITIES_URLS_FILE    = os.path.join(CWD, "cities_urls.pkl")

DB_HOST             = os.getenv("CONSOLE_COWBOYS_MONGO_HOST")
DB_USER             = os.getenv("CONSOLE_COWBOYS_MONGO_USER")
DB_PASS             = os.getenv("CONSOLE_COWBOYS_MONGO_PASS")
DB_PORT             = os.getenv("CONSOLE_COWBOYS_MONGO_PORT")
DB_NAME             = os.getenv("CONSOLE_COWBOYS_MONGO_NAME")


def save_hiring_startup(startup_info):

    """
    Visits a startup's website and checks if it has a careers page.
    Every <a> tag in that page is tested against a list of keywords.
    If jobs page is found, its url is added as a "jobs_page" key
    on the startup_info dictionary.
    We then append startup_info to a pickle file inside the hiring_startups
    directory under the name hiring_<location>.pkl
    """

    startup_name     = startup_info["name"]
    startup_url      = startup_info["url"]
    location         = startup_info["location"]

    hiring_file_path = os.path.join(
                            HIRING_STARTUPS_DIR,
                            "{}.pkl".format(location)
                        )

    site_data = helpers.soupify_website(startup_url)

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


def get_all_software_jobs_links(startup_info):

    """
    Similar to save_hiring_startup, this function will call
    helpers.extract_software_jobs_links passing it the startup's jobs page
    Every link in that page will be tested against a list of keywords.
    jobs_links stores the result of calling that function (a list of dicts
    containing job titles and urls for every match found)
    If the list of found jobs is greater than 0.
    We add the list to the startup_info dictionary as "job_listing_urls"
    then return the startup object.
    """

    jobs_page   = startup_info["jobs_page"]
    jobs_links  = helpers.extract_software_job_links(jobs_page)

    if len(jobs_links) > 0:
        logger.info("{} is hiring devs in {}".format(
            startup_info["name"],
            startup_info["location"],
        ))
        startup_info["job_listing_urls"] = jobs_links
        return startup_info


def get_startup_list_for_a_city(url):

    """
    Extract the list of startups for every location.startups-list.com website.
    """

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
    file_path       = os.path.join(STARTUPS_INFO_DIR, file_name)

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

    # Connect to MongoDB and authenticate to the database using the credentials
    db = JobsDB(DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME)
    db.connect()

    # If cities_url.pkl does not exist (ie. we're running the script for the
    # 1st time or the file was deleted for some reason)
    # We call get_all_cities() this is so because we don't want to make
    # unnecessary network calls every time the script is run.

    if not os.path.exists(CITIES_URLS_FILE):
        get_all_cities()

    logger.info("Found cities_urls.pkl, proceeding to load the data ...")

    # At this point the file either already exists or it has been created
    # so we load its content into cities_urls.
    with open(CITIES_URLS_FILE, "rb") as cities_urls_file:
        cities_urls = pickle.load(cities_urls_file)

    logger.info("Urls loaded !")

    # If the startups_info directory does not exist (or was deleted),
    # we create it and use a Pool of processes to save the list of startups
    # for every location in cities_url (which is a list)
    # Essentially, multiple processes will be spawned calling
    # get_startup_list_for_a_city(url from cities_url)

    if not os.path.isdir(STARTUPS_INFO_DIR):

        logger.info("Creating startups_info directory")
        os.mkdir(STARTUPS_INFO_DIR)
        logger.info("startups_info directory created")

        logger.info("Fetching startup list for all cities ...")

        with multiprocessing.Pool() as pool:
            result = pool.map(get_startup_list_for_a_city, cities_urls)

    # The startups_info directory was created or already exists
    logger.info("Found startup_info directory. Loading filenames ...")

    # We load all the files in ./startups_info and save them in
    # startups_filenames
    startup_filenames   = [file for file in os.listdir(STARTUPS_INFO_DIR)]

    # We check to see if the hiring_startups directory exists
    # If it does not, we create it just like we did previously.
    # Then, looping through each file in the startups_filename list
    # we use multiprocessing to call save_hiring_startup passing in the
    # startup_list

    if not os.path.isdir(HIRING_STARTUPS_DIR):

        logger.info("Creating hiring_startups directory")
        os.mkdir(HIRING_STARTUPS_DIR)
        logger.info("startups_info directory created")

        logger.info("Checking startups for open jobs ...")

        for filename in startup_filenames:

            file_path = os.path.join(STARTUPS_INFO_DIR, filename)

            with open(file_path, "rb") as startup_info_file:
                startup_list = pickle.load(startup_info_file)

            with multiprocessing.Pool() as pool:
                pool.map(save_hiring_startup, startup_list)

        logger.info("Done checking startups for open jobs")

    logger.info("Found hiring_startups directory. Loading files ...")

    # We should now have a hiring_startups directory populated pickle files
    # containing information about startups hiring developers
    # We load the list of files in hiring_startups_files
    hiring_startups_files = [file for file in os.listdir(HIRING_STARTUPS_DIR)]

    # After that we loop through each file
    for filename in hiring_startups_files:

        # extract the city from the filename
        city = filename.split(".")[0].split("_")[1]

        # set the correct file path
        file_path = os.path.join(HIRING_STARTUPS_DIR, filename)

        # We create two lists here : startups_with_open_jobs
        # and startups_hiring_devs (the latter will contain the filtered list of
        # startups along with details about each job listing found)

        # The reason for startups_with_open_jobs is that the files we're
        # currently looping through don't contain a list like before. They
        # contain objects that were appended by calling save_hiring_startup

        # As a result we have to infinetely loop through the pickle file to load
        # the startups one at a time until we reach the end of the file.
        # We then append each startup to the list so we can have an iterable to
        # pass to our get_all_software_jobs_links function because it will be
        # called in a multiprocessing pool

        startups_with_open_jobs = []
        startups_hiring_devs = []

        with open(file_path, "rb") as hiring_startups_file:

            logger.info(
                "Loading list of startups with open jobs in {}".format(
                    city
                )
            )

            while True:

                try:
                    startup = pickle.load(hiring_startups_file)
                    startups_with_open_jobs.append(startup)
                except EOFError as e:
                    logger.info("All {} startups loaded".format(city))
                    break

        logger.info("Filtering {} startups for software jobs ...".format(city))

        with multiprocessing.Pool() as pool:
            # get_all_software_jobs_links returns either the startups_info dict
            # or None in the case where no software jobs were found so we have
            # to filter the startups_with_open_jobs list and remove all the None
            # values.

            startups_hiring_devs = list(filter(
                lambda x: x is not None,
                pool.map(get_all_software_jobs_links, startups_with_open_jobs)
            ))

            logger.info(
                "Total number of startups hiring devs in {} - {}".format(
                    city,
                    len(startups_hiring_devs)
                )
            )

        # Finally, we insert the jobs in the database.
        db.insert_jobs(startups_hiring_devs, city)

    logger.info("Finished")
