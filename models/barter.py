from models.Databasemodel import Database

class RequestId(object):
    def __init__(self, overall, _id='request'):
        self.overall=overall
        self._id=_id
    
    @classmethod
    def find(cls):
        data=Database.search_one_user("barter",{'_id':'request'})
        return cls(**data)
    
    @classmethod
    def check_existence(cls,idd):
        data= Database.search_one_user("barter", {"_id": idd})
        if data is not None:
            return cls(**data)
        else:
            return None
    
    @classmethod
    def create(cls):
        overall=0
        new = cls(overall)
        new.save_to_mongo()


    @staticmethod
    def update():
        data=RequestId.find()
        data.overall=data.overall+1
        Database.update_user("barter",{"_id":data._id}, {"$set":{"overall":data.overall}})
    
    @staticmethod
    def get_number():
        data=RequestId.check_existence('request')
        if data is not None:
            return data.overall
        else:
            RequestId.create()
            data=RequestId.find()
            return data.overall

    def json(self):
        return {
            '_id' : self._id,
            'overall' : self.overall
        }
    
    def save_to_mongo(self):
        Database.save("barter", self.json())


class BarterRequest(object):
    def __init__(self, request_number, to_email, service_type, details, from_email, services_offered, comments=[], status='In Progress', _id=None):
        self.request_number=request_number
        self.to_email=to_email
        self.service_type=service_type
        self.details=details
        self.from_email=from_email
        self.services_offered=services_offered
        self.comments=comments
        self.status=status
        self._id=_id
    
    @classmethod
    def search_for_new_request(cls, requester_email, requestee_email, service_type_requested, service_requested_details):
        data = Database.search("barter", {"from_email":requester_email})
        result=list(data)
        if len(result)==0:
            return True
        else:
            i=0
            for w in result:
                if w['to_email']==requestee_email and w['service_type']==service_type_requested and w['details']==service_requested_details and w['status']=='In Progress':
                    i=1
                    break
                else:
                    continue
            
            if i==0:
                return True
            else:
                return False

    @classmethod
    def barter_request(cls, number, to_email, from_email, service_type, details, services_offered):
        check=BarterRequest.search_for_new_request(from_email, to_email, service_type, details)
        if check:
            new_request=cls(number,to_email, service_type, details, from_email, services_offered)
            new_request.save_request()
            return True
        else:
            return False
    
    @staticmethod
    def get_requests_sent(email):
        data=Database.search("barter", {"from_email":email})
        result=list(data)
        reqs=[]
        for w in result:
            if w['status']=='In Progress':
                reqs.append(w)
            else:
                continue
        return reqs
    
    @staticmethod
    def get_requests_received(email):
        data=Database.search("barter", {"to_email":email})
        result=list(data)
        reqs=[]
        for w in result:
            if w['status']=='In Progress':
                reqs.append(w)
            else:
                continue
        return reqs

    @staticmethod
    def get_requests_accepted(email):
        data1=Database.search("barter", {"to_email":email})
        result1=list(data1)
        data2=Database.search("barter",{"from_email":email})
        result2=list(data2)
        reqs=[]
        for w in result1:
            if w['status']=='Accepted':
                reqs.append(w)
            else:
                continue
        for a in result2:
            if a['status']=='Accepted':
                reqs.append(a)
            else:
                continue
        return reqs

    @staticmethod
    def get_requests_declined(email):
        data1=Database.search("barter", {"to_email":email})
        result1=list(data1)
        data2=Database.search("barter", {"from_email":email})
        result2=list(data2)
        reqs=[]
        for w in result1:
            if w['status']=='Declined':
                reqs.append(w)
            else:
                continue
        for a in result2:
            if a['status']=='Declined':
                reqs.append(a)
            else:
                continue
        return reqs

    @classmethod
    def search_request(cls, request_number):
        data= Database.search_one_user("barter", {"request_number":request_number})
        if data is not None:
            return cls(**data)
        else:
            return False

    @staticmethod
    def add_comments(request_number, new_comments):
        data=BarterRequest.search_request(request_number)
        if data:
            data.comments.append(new_comments)
            Database.update_user("barter",{"request_number":data.request_number}, {"$set":{"comments":data.comments}})
            return True
        else:
            return False

    @staticmethod
    def received_comments(request_number, flag, new_comments):
        data=BarterRequest.search_request(request_number)
        print(flag)
        if data:
            if flag==0:
                data.comments.append(new_comments)
                Database.update_user("barter",{"request_number":data.request_number}, {"$set":{"comments":data.comments}})
                return True
            elif flag==1:
                data.comments.append(new_comments)
                data.status='Accepted'
                Database.update_user("barter",{"request_number":data.request_number}, {"$set":{"comments":data.comments}})
                Database.update_user("barter",{"request_number":data.request_number}, {"$set":{"status":data.status}})
                return True
            else:
                data.comments.append(new_comments)
                data.status='Declined'
                Database.update_user("barter",{"request_number":data.request_number}, {"$set":{"comments":data.comments}})
                Database.update_user("barter",{"request_number":data.request_number}, {"$set":{"status":data.status}})
                return True
        else:
            return False

    def json(self):
        return {
            'request_number':self.request_number,
            'to_email' : self.to_email,
            'service_type' : self.service_type,
            'details' : self.details,
            'from_email' : self.from_email,
            'services_offered' : self.services_offered,
            'comments' : self.comments,
            'status':self.status
        }
    
    def save_request(self):
        Database.save("barter", self.json())




