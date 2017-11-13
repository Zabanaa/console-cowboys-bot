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


class TestDB():

    def test_create_connection(self):

        db = JobsDB(DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME, 2000)
        connection = db.connect()
        assert isinstance(connection, MongoDatabase)
        assert DB_NAME == db.dbname == connection._Database__name


    def test_failed_connection(self):
        # Invalid host and port
        with pytest.raises(SystemExit) as exc:
            db = JobsDB("superman", "clark123",
                        "1.2.3.4", 23454, "supermandb", 2000)
            connection = db.connect()

        exception_message = exc.value.args[0]
        expected_err_msg = "Connection Error. Please check the host and port."
        assert exception_message == expected_err_msg


    def test_failed_authentication(self):
        # Invalid password
        with pytest.raises(SystemExit) as exc:
            db = JobsDB(DB_USER, "clark123",
                        DB_HOST, DB_PORT, DB_NAME, 2000)
            connection = db.connect()

        exception_message = exc.value.args[0]
        expected_err_msg = "Please ensure credentials are valid."

        assert expected_err_msg in exception_message


    def test_insert_jobs(self):
        pass
