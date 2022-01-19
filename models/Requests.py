from models.Databasemodel import Database

class Requests(object):
    def __init__(self, received, _id='request'):
        self.received=received
        self._id= _id
    
    @classmethod
    def check_existence(cls,idd):
        data= Database.search_one_user("requests", {"_id": idd})
        if data is not None:
            return cls(**data)
        else:
            return None
    
    @classmethod
    def create(cls):
        received=[]
        new = cls(received)
        new.save_to_mongo()

    @classmethod
    def request(cls, request):
        check='request'
        req=Requests.check_existence(check)
        if req is not None:
            req.received.append(request)
            Database.update_user("requests", {"_id":req._id}, {"$set":{"received":req.received}})
            return req
        else:
            Requests.create()
            req= Requests.check_existence(check)
            req.received.append(request)
            Database.update_user("requests", {"_id":req._id}, {"$set":{"received":req.received}})
            return req
    
    def json(self):
        return {
            '_id' : self._id,
            'received' : self.received
        }
    
    def save_to_mongo(self):
        Database.save("requests", self.json())