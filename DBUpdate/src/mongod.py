from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

class MongoDBManager:
    def __init__(self, uri):
        self.uri = uri
        self.connection = None

    def get_connection(self):
        if not self.connection:
            try:
                self.connection = MongoClient(self.uri, server_api=ServerApi('1'))
            except Exception as e:
                print(f'Could not connect to MongoDB: {e}')
        return self.connection

    def add_match(self, matchData):
        if not self.get_connection():
            return False

        if 'metadata' in matchData and 'matchId' in matchData['metadata']:
            coll = self.get_connection().get_database('leagueoflegends').get_collection('matches')
            count = coll.count_documents({'metadata.matchId': matchData['metadata']['matchId']})
            if count == 0:
                coll.insert_one(matchData)
                return True
        else:
            print("Invalid match data encountered and skipped.")


    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None
