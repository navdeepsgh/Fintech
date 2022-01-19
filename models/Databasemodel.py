import pymongo
from pymongo import MongoClient

class Database(object):
    URI = "mongodb+srv://navdeep:navdeep@fintech.nwmsa.mongodb.net/fintech?retryWrites=true&w=majority"
    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client['fullstack']
    
    @staticmethod
    def save(collection, data):
        Database.DATABASE[collection].insert(data)
    
    @staticmethod
    def search(collection, query):
        return Database.DATABASE[collection].find(query)
    
    @staticmethod
    def search_one_user(collection, query):
        return Database.DATABASE[collection].find_one(query)
    
    @staticmethod
    def update_user(collection, query, update):
        return Database.DATABASE[collection].update(query, update)

