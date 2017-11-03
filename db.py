from pymongo import MongoClient
from pymongo.errors import OperationFailure

def connect(user, password, host, port, dbname):
    client = MongoClient(host=host, port=port)
    db     = client[dbname]

    try:
        db.authenticate(name=user, password=password)
    except OperationFailure as e:
        error = e.details["errmsg"]
        message =  "Please ensure that the credentials passed are valid."
        raise Exception("{} {}".format(error, message))
    else:
        return db

def insert_jobs(db, jobs):

    try:
        jobs_inserted = db.jobs.insert_many(jobs)
    except Exception as e:
        raise Exception("Something Happened {}".format(e))
    else:
        return jobs_inserted.inserted_ids

