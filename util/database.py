from pymongo import MongoClient
import bcrypt

mongo_client = MongoClient("mongo")
db = mongo_client["CSE312_666"]
chat_collection = db["Chat_room"]
posts_collection = db["Posts"]
replies_collection = db['Replies']
cred_collection = db["cred"]

def get_useremail(request):
    auth_cook = request.cookies.get('auth_token')
    if auth_cook != None and auth_cook != "":
        for doc in cred_collection.find({},{'_id' : False}):
            if "auth_token" in doc.keys() and doc["auth_token"] != '' and bcrypt.checkpw(auth_cook.encode(),doc["auth_token"]):
                return doc["email"]
    return 'Guest'

def find_user(data:dict):
    return cred_collection.find_one(data)

def find_usr_name(data:dict):
    doc = cred_collection.find_one(data)
    if doc != None and "email" in doc:
        return doc['email']

def add_user(data:dict):
    cred_collection.insert_one(data)

def updata_user_doc(key:dict, updata_doc:dict):
    cred_collection.update_one(key,{"$set":updata_doc})

def valid_user_name(email:str):
    if email == "" or email == 'Guest':
        return None
    else:
        return find_user({'email':email})
    
def get_all_post():
    return list(posts_collection.find())

def get_user_email(request):
    auth_cook = request.cookies.get('auth_token')

    if auth_cook != None and auth_cook != "":
        for doc in cred_collection.find({},{'_id' : False}):

            if "auth_token" in doc.keys() and doc["auth_token"] != '' and bcrypt.checkpw(auth_cook.encode(),doc["auth_token"]):
                return doc["email"]
    return 'Guest'

def find_all_cred():
    return cred_collection.find()