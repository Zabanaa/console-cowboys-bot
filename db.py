import logging
import sys

from pymongo import MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

class JobsDB(object):

    """
    This class will be used to connect to MongoDB, authenticate to a database
    and insert jobs in it.
    """

    def __init__(self, user, password, host, port, dbname):
        self.user = user
        self.password = password
        self.host = host
        self.port = int(port)
        self.dbname = dbname

    def connect(self):

        # 1 - Establish a connection to the MongoDB server

        logger.info("Attempting connection to MongoDB server ...")

        try:
            client = MongoClient(host=self.host, port=self.port)
        except TypeError as e:
            logger.error("Error: {}".format(e))
            return
        else:
            self.db = client[self.dbname]

        logger.info("Connection to MongoDB server established !")

        # 2 - Authenticate user using passed credentials

        logger.info("Logging into the database ...")

        try:
            self.db.authenticate(name=self.user, password=self.password)
        except OperationFailure as e:
            error = e.details["errmsg"]
            message = "Please ensure that the credentials passed are valid."
            logger.error("{} {}".format(error, message))
            sys.exit()
        except ServerSelectionTimeoutError as e:
            logger.error("Connection Error. Please check the host and port.")
            sys.exit()
        else:
            logger.info("Connected to the database !")
            return self.db

    def insert_jobs(self, jobs_list, city):

        """
        Attempts to insert the jobs_list in the databse calling insert_many
        Exits on failure.
        """

        try:
            logger.info("Inserting {} startups jobs".format(city))
            jobs_inserted = self.db.jobs.insert_many(jobs_list)
        except Exception as e:
            logger.error("Error inserting jobs. Reason: {}".format(e))
            sys.exit()
        else:
            logger.info("Inserted {} jobs in the database.".format(
                len(jobs_inserted.inserted_ids)
            ))
