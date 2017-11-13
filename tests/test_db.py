import os
import pytest
from consolecowboys_scraper.db import JobsDB
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.database import Database as MongoDatabase


DB_HOST             = os.getenv("CONSOLE_COWBOYS_MONGO_HOST")
DB_USER             = os.getenv("CONSOLE_COWBOYS_MONGO_USER")
DB_PASS             = os.getenv("CONSOLE_COWBOYS_MONGO_PASS")
DB_PORT             = os.getenv("CONSOLE_COWBOYS_MONGO_PORT")
DB_NAME             = os.getenv("CONSOLE_COWBOYS_MONGO_NAME")


class TestDB(object):


    def setup_method(self):
        self.db = JobsDB(DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME, 2000)
        self.connection = self.db.connect()

    def teardown_method(self):
        self.connection.client.close()

    def test_create_connection(self):
        assert isinstance(self.connection, MongoDatabase)
        assert DB_NAME == self.db.dbname == self.connection._Database__name

    def test_failed_connection(self):

        with pytest.raises(SystemExit) as exc:
            # override self.db with invalid host and port information
            self.db = JobsDB("superman", "clark123",
                        "1.2.3.4", 23454, "supermandb", 2000)
            self.connection = self.db.connect()

        exception_message = exc.value.args[0]
        expected_err_msg = "Connection Error. Please check the host and port."
        assert exception_message == expected_err_msg


    def test_failed_authentication(self):
        with pytest.raises(SystemExit) as exc:
            # override self.db with invalid password
            self.db = JobsDB(DB_USER, "clark123",
                        DB_HOST, DB_PORT, DB_NAME, 2000)
            self.connection = self.db.connect()

        exception_message = exc.value.args[0]
        expected_err_msg = "Please ensure credentials are valid."

        assert expected_err_msg in exception_message


    def test_insert_jobs(self):
        jobs = [{"hello": "world"}, {"name": 123}]
        inserted_jobs = self.db.insert_jobs(jobs, "new-york")

        assert len(inserted_jobs) == len(jobs)

    def test_insert_jobs_fail(self):
        # find a way to make the bloody test fail
        pass
