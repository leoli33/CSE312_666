from pymongo import MongoClient
import bcrypt, hashlib

mongo_client = MongoClient("mongo")
db = mongo_client["CSE312_666"]
chat_collection = db["Chat_room"]
posts_collection = db["Posts"]
replies_collection = db['Replies']
cred_collection = db["cred"] # keys: email, password, photo_path, new_username, auth_token, id
id_collection = db["unique_id"]

def get_id():
   doc = id_collection.find_one_and_update({}, {"$inc": {"id": 1}}, upsert=True, return_document=True)
   return doc["id"]

def valid_login(email: str, password: str):
    cred = cred_collection.find_one({"email": email})
    if cred == None:
        return False
    return bcrypt.checkpw(password.encode(), cred["password"])

def delete_token(request):
    if 'auth_token' in request.cookies:
        token = request.cookies.get('auth_token')
        hash_token = hashlib.sha256(token.encode()).hexdigest()
        cred_collection.update_one({"token": hash_token}, {"$unset": {"token": ""}})

def get_user_email(request):
    if 'auth_token' in request.cookies:
        token = request.cookies.get('auth_token')
        hash_token = hashlib.sha256(token.encode()).hexdigest()
        data = cred_collection.find_one({"token": hash_token}, {"_id": 0})
        if data != None:
            return data['email']
    return 'Guest'

def find_user(email: str):
    data = cred_collection.find_one({'email': email})
    if data == None:
        return False
    return data

def add_user(data:dict):
    cred_collection.insert_one(data)

def update_user_doc(key:dict, new_key:dict):
    cred_collection.update_one(key, {"$set": new_key})
    
def get_all_post():
    return list(posts_collection.find())

def get_all_post_raw():
    return posts_collection
