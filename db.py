from pymongo import MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError


class JobsDB(object):

    def __init__(self, user, password, host, port, dbname):
        self.user = user
        self.password = password
        self.host = host
        self.port = int(port)
        self.dbname = dbname

    def connect(self):

        # 1 - Establish a connection to the MongoDB server

        try:
            client = MongoClient(host=self.host, port=self.port)
        except TypeError as e:
            # This should be logged instead
            print("Error: {}".format(e))
            return
        else:
            self.db = client[self.dbname]

        # 2 - Authenticate user using passed credentials

        try:
            self.db.authenticate(name=self.user, password=self.password)
        except OperationFailure as e:
            error = e.details["errmsg"]
            message = "Please ensure that the credentials passed are valid."
            raise Exception("{} {}".format(error, message))
        except ServerSelectionTimeoutError as e:
            print("Connection Error. Please check the host and port.")
        else:
            return self.db

    def insert_jobs(self, jobs_list):

        try:
            jobs_inserted = self.db.jobs.insert_many(jobs_list)
        except Exception as e:
            raise Exception("Error inserting jobs. Reason: {}".format(e))
        else:
            return jobs_inserted.inserted_ids
