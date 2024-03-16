
from flask import Flask, request, render_template, send_from_directory, jsonify, redirect, url_for, flash, make_response, session

from flask_socketio import SocketIO
from pymongo import MongoClient
import bcrypt
import string
import random

mongo_client = MongoClient("mongo")
db = mongo_client["CSE312_666"]
chat_collection = db["Chat_room"]
cred_collection = db["cred"]

app = Flask(__name__)
socketio = SocketIO(app)

@app.after_request
def security(response):
   response.headers['X-Content-Type-Options'] = 'nosniff'
   return response

@app.route('/')
def index():
   return render_template('index.html')

@app.route('/home')
def home():

    auth_cook = request.cookies.get('auth_token')

    if auth_cook != None and auth_cook != "":
        for doc in cred_collection.find({},{'_id' : False}):

            if "auth_token" in doc.keys() and doc["auth_token"] != '' and bcrypt.checkpw(auth_cook.encode(),doc["auth_token"]):
                user_email = session.get("{{user_email}}", None)
                return render_template('home.html', user_email=doc["email"])
                
                #return render_template('home.html')
    
    return render_template('home_notloggedin.html')

@app.route('/post')
def post():
    return render_template('post.html')


@app.route('/signup_page')
def signup_page():
     return render_template('index_signup.html')

@app.route('/signup', methods=['POST'])
def signup():

    if request.method == 'POST':

        email = str(request.form['email'])
        password = str(request.form['password'])
        confirm_pass = str(request.form['password_confirm'])


        if cred_collection.find_one({'email': email}): #check email exists
          
            return render_template('index_signup.html')
        else:

            if password != confirm_pass: #password does not match
                return render_template('index_signup.html')
            
            else: #success
                hashed_pass = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                cred_collection.insert_one({"email":email,"password":hashed_pass})
                return redirect(url_for('index'))
        

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':

        email = str(request.form['email'])
        password = str(request.form['password'])

        for doc in cred_collection.find({},{'_id' : False}):

            if email == doc["email"] and bcrypt.checkpw(password.encode(),doc["password"]): #can log in

                print(request.cookies.get('auth_token') )

                #auth_cook = request.cookies.get('auth_token')

                N = 20
                auth_tok = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=N))
                hashed_token = bcrypt.hashpw(auth_tok.encode(), bcrypt.gensalt())

                if "auth_token" in doc.keys(): #already has token in db

                    cred_collection.update_one({"email":doc["email"] ,"password":doc["password"],"auth_token":doc["auth_token"]}, {"$set":{"email" : doc["email"],  "password" : doc["password"], "auth_token": hashed_token}})

                    response = make_response(redirect(url_for('home')))
                    response.set_cookie('auth_token', auth_tok, max_age = 3600, httponly = True)
                    return response
                    
                
                else: #never had token in db
                    cred_collection.update_one({"email":doc["email"] ,"password":doc["password"]}, {"$set":{"email" : doc["email"],  "password" : doc["password"], "auth_token": hashed_token}})

                    response = make_response(redirect(url_for('home')))
                    response.set_cookie('auth_token', auth_tok, max_age = 3600, httponly = True)
                    return response
            
        return redirect(url_for('index')) #login failed

@app.route('/logout',methods = ['POST','GET'])
def logout():
    if request.method == "GET":

        auth_cook = request.cookies.get('auth_token')

        for doc in cred_collection.find({},{'_id' : False}):

            if "auth_token" in doc.keys() and doc["auth_token"] != '' and bcrypt.checkpw(auth_cook.encode(),doc["auth_token"]):

                cred_collection.update_one({"email":doc["email"] ,"password":doc["password"],"auth_token":doc["auth_token"]}, {"$set":{"email" : doc["email"],  "password" : doc["password"], "auth_token": ""}})
                response = make_response(redirect(url_for('index')))
                response.set_cookie('auth_token', "", expires = 0, httponly = True)
                return response

@app.route('/message', methods=['GET', 'POST', 'PUT'])
def message():
    if request.method == 'GET':
        return render_template('message.html')
    elif request.method == 'POST':
        data = request.get_json()
        return jsonify({'message': '201 Created'}), 201
    elif request.method == 'PUT':
        return jsonify({'message': '200 OK'}), 200
    else:
        return jsonify({'message': '404 Not Found'}), 404


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=8080)
