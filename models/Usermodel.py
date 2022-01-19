from flask import session
from models.Databasemodel import Database
from passlib.hash import sha256_crypt

class User(object):
    def __init__(self, name, age, gender, occupation, email, password, services_offered, services_requested=[], _id=None):
        self.name=name   
        self.age=age
        self.gender=gender
        self.occupation=occupation
        self.email=email
        self.password=password
        self.services_offered=services_offered
        self.services_requested=services_requested
        self._id=_id
    
    @classmethod
    def search_for_login(cls, email):
        data = Database.search_one_user("users", {"email":email})
        if data is not None:
            return cls(**data)
    
    @classmethod
    def search_for_signup(cls, email):
        data = Database.search_one_user("users", {"email":email})
        if data is not None:
            return False
        else:
            return True
    
    @classmethod
    def search_user(cls, email):
        data= Database.search_one_user("users", {"email":email})
        return cls(**data)
    
    @staticmethod
    def validate_login(email, password):
        user=User.search_for_login(email)
        if user is not None:
            return sha256_crypt.verify(password, user.password)
        return False
    
    @staticmethod
    def search_users_by_service(search_type):
        customers=Database.search("users", {"services_offered":{"$elemMatch":{"type_of_service":search_type}}})
        result=list(customers)
        return result
    
    @classmethod
    def signup_user(cls, name, age, gender, occupation, email, password, services_offered):
        user=User.search_for_signup(email)
        if user:
            new_user=cls(name, age, gender, occupation, email, password, services_offered)
            new_user.save_user()
            session['email']=email
            return True
        else:
            return False
    
    @staticmethod
    def login(email):
        session['email']=email
    
    @staticmethod
    def logout():
        session['email']=None
    
    @staticmethod
    def add_service(new_service, email):
        current_user=User.search_user(email)
        current_user.services_offered.append(new_service)
        Database.update_user("users", {"email":current_user.email}, {"$set":{"services_offered":current_user.services_offered}})
        return True
    
    @staticmethod
    def request_service(requestt, email):
        current_user=User.search_user(email)
        current_user.services_requested.append(requestt)
        Database.update_user("users",{"email":current_user.email}, {"$set":{"services_requested":current_user.services_requested}})
        return True
    
    @staticmethod
    def update_services_offered(email,services):
        current_user=User.search_user(email)
        current_user.services_offered=services
        Database.update_user("users",{"email":current_user.email}, {"$set":{"services_offered":current_user.services_offered}})
        return True

    def json(self):
        return {
            'name' : self.name,
            'age' : self.age,
            'gender' : self.gender,
            'occupation' : self.occupation,
            'email' : self.email,
            'password' : self.password,
            'services_offered':self.services_offered,
            'services_requested':self.services_requested
        }
    
    def save_user(self):
        Database.save("users", self.json())
