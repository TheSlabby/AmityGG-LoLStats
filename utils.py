from pymongo import MongoClient

uri = open('.key', 'r').readlines()[2].strip()

def get_db_handle():
    client = MongoClient(uri)
    return client
