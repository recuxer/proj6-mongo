"""
author: John Nemeth
sources: Heavy reference from starter code, previous assignments
description: file for database functions to be used by flask_main
"""

#import pymongo
from pymongo import MongoClient
import arrow

#for config variables
import flask_main

#mongo URL
MONGO_CLIENT_URL = "mongodb://{}:{}@{}:{}/{}".format(
    flask_main.CONFIG.DB_USER,
    flask_main.CONFIG.DB_USER_PW,
    flask_main.CONFIG.DB_HOST, 
    flask_main.CONFIG.DB_PORT, 
    flask_main.CONFIG.DB)
print("Using URL '{}'".format(MONGO_CLIENT_URL))

# database connection for every server process
try: 
    dbclient = MongoClient(MONGO_CLIENT_URL)
    db = getattr(dbclient, flask_main.CONFIG.DB)
    collection = db.dated
except:
    print("Failure opening database.  Is Mongo running? Correct password?")
    sys.exit(1)

##########
# database functions accessed by flask_main

#func to enter in DB
def enterinDB(memo, datetime):
    memotime = arrow.get(datetime, 'YYYY-MM-DD HH:mm')
    newmemo = { "type": "dated_memo",
                "date": memotime.naive,
                "text": memo
              }
    collection.insert_one(newmemo)

#func to remove from DB
def removefromDB(datetime):
    memodate = arrow.get(datetime).naive
    collection.delete_one({ "date": memodate})

#func to return list of memos
def getmemos():
    records = []
    for record in collection.find({ "type": "dated_memo" }).sort('date'):
        record['date'] = arrow.get(record['date']).isoformat()
        del record['_id']
        records.append(record)
    return records
