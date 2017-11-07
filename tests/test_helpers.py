from consolecowboys_scraper import helpers

class TestHelpers(object):

    def test_extract_city_name(self):

        url = "http://atlanta.startups-list.com"
        city_name = helpers.extract_city_name(url)
        assert city_name == "atlanta"

        url = "http://nycstartups.com"
        city_name = helpers.extract_city_name(url)
        assert city_name == "new-york"

        url = "http://startupsinnyc.com"
        city_name = helpers.extract_city_name(url)
        assert city_name == "new-york"

        url = "http://startupsla.com"
        city_name = helpers.extract_city_name(url)
        assert city_name == "los-angeles"

        url = "http://mtlstartups.com"
        city_name = helpers.extract_city_name(url)
        assert city_name == "montreal"

        url = "http://bostonstartups.com"
        city_name = helpers.extract_city_name(url)
        assert city_name == "boston"

        url = "http://chicagostartups.com"
        city_name = helpers.extract_city_name(url)
        assert city_name == "chicago"

    def test_set_file_name_to_city_name(self):

        city_name = "montreal"
        file_name = helpers.set_file_name_to_city_name(city_name)
        assert file_name == "{}.pkl".format(city_name)

    def test_remove_trailing_slash(self):
        clean_url = "https://twitter.com/zabanaa_/"
        assert helpers.remove_trailing_slash(clean_url + "/") == clean_url

    def test_handle_local_links(self):
        url = "http://youtube.com"
        local_link = "/careers/engineering"
        final_link = helpers.handle_local_links(url, local_link)

        assert final_link == url + local_link

        local_link = "careers/marketing"
        final_link = helpers.handle_local_links(url, local_link)
        assert final_link == url + "/" +local_link

    def test_soupify_website(self):
        pass

    # These tests will require mocking of either request or BeautifulSoup
    def test_startup_has_jobs(self):
        pass

    def test_extract_software_jobs_links(self):
        # assert function called soupify_website with the correct url
        pass
