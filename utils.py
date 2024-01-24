from pymongo import MongoClient

uri = open('.key', 'r').readlines()[0].strip()

def get_db_handle():
    client = MongoClient(uri)
    return client
