
from flask import Flask, request, render_template, send_from_directory, jsonify, redirect, url_for, flash, make_response, session, session

from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import pymongo
import bcrypt
import string
import random

mongo_client = MongoClient("mongo")
db = mongo_client["CSE312_666"]
chat_collection = db["Chat_room"]
posts_collection = db["Posts"]
replies_collection = db['Replies']
cred_collection = db["cred"]


app = Flask(__name__)
app.secret_key = '4d56sad5a1c23xs'
socketio = SocketIO(app)

def check_login():
    # Check if the auth token is in the session
    if 'auth_token' not in request.cookies:
        # Redirect to the login page if the auth token is not present
        return redirect(url_for('login'))
    else:
        # Check if the auth token is valid (e.g., validate against database or other storage)
        auth_token = request.cookies.get('auth_token')
        if not validate_auth_token(auth_token):  # Implement this function to validate the auth token
            return redirect(url_for('login'))

def validate_auth_token(auth_token):
    # Implement logic to validate the auth token, e.g., check against database
    # Return True if the token is valid, False otherwise
    # Example pseudo code:
    # user = User.query.filter_by(auth_token=auth_token).first()
    # return user is not None
    return True  # Placeholder, replace with actual validation logic

@app.before_request
def before_request():
    # Call the function to check if the user is logged in before each request
    check_login()
    
@app.after_request
def security(response):
   response.headers['X-Content-Type-Options'] = 'nosniff'
   return response

@app.route('/')
def index_html():
   return render_template('index.html')

@app.route('/home')
def home():

    auth_cook = request.cookies.get('auth_token')

    if auth_cook != None and auth_cook != "":
        for doc in cred_collection.find({},{'_id' : False}):

            if "auth_token" in doc.keys() and doc["auth_token"] != '' and bcrypt.checkpw(auth_cook.encode(),doc["auth_token"]):
                user_email = session.get("{{user_email}}", None)
                return render_template('home.html', user_email=doc["email"])
    
    return render_template('home.html', user_email='Guest')

@app.route('/signup_page')
def signup_page():
     return render_template('register.html')

@app.route('/signup', methods=['POST'])
def signup():

    if request.method == 'POST':

        email = str(request.form['email'])
        password = str(request.form['password'])
        confirm_pass = str(request.form['password_confirm'])


        if cred_collection.find_one({'email': email}): #check email exists
          
            return render_template('register.html')
        else:

            if password != confirm_pass: #password does not match
                return render_template('register.html')
            
            else: #success
                hashed_pass = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                cred_collection.insert_one({"email":email,"password":hashed_pass})
                return redirect(url_for('index_html'))
        

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':

        email = str(request.form['email'])
        password = str(request.form['password'])
        session['user_email'] = 'user@example.com'
        # print("default email: ", session['user_email'])

        for doc in cred_collection.find({},{'_id' : False}):

            if email == doc["email"] and bcrypt.checkpw(password.encode(),doc["password"]): #can log in

                print(request.cookies.get('auth_token') )

                #auth_cook = request.cookies.get('auth_token')
                session['user_email'] = doc["email"]
                # print("actual email: ", session['user_email'])

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
            
        return redirect(url_for('index_html')) #login failed

@app.route('/logout',methods = ['POST','GET'])
def logout():
    if request.method == "GET":

        auth_cook = request.cookies.get('auth_token')

        for doc in cred_collection.find({},{'_id' : False}):

            if "auth_token" in doc.keys() and doc["auth_token"] != '' and bcrypt.checkpw(auth_cook.encode(),doc["auth_token"]):

                cred_collection.update_one({"email":doc["email"] ,"password":doc["password"],"auth_token":doc["auth_token"]}, {"$set":{"email" : doc["email"],  "password" : doc["password"], "auth_token": ""}})
                response = make_response(redirect(url_for('index_html')))
                response.set_cookie('auth_token', "", expires = 0, httponly = True)
                return response

##################发帖子相关 function##################
@app.route('/explore')
def posts_list_html():
    user_email = session.get('user_email', None) 
    if not user_email:
        flash('Please log in to see your posts.') 
        return redirect(url_for('login'))
    
    all_posts = list(posts_collection.find())
    for post in all_posts:
        content = post.get('content', '')
        post['content_preview'] = content.split('\n')[0] if content else ''
        
        if 'timestamp' in post:
            post['posting_time'] = post['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            post['posting_time'] = post['_id'].generation_time.strftime('%Y-%m-%dT%H:%M:%SZ') 
        
        last_reply = replies_collection.find_one(
            {'threadId': ObjectId(post['_id'])}, 
            sort=[('timestamp', pymongo.DESCENDING)]
        )
        if last_reply:
            post['last_reply_time'] = last_reply['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            post['last_reply_time'] = post['posting_time']
    return render_template('post.html', posts=all_posts)

@app.route('/submit-post', methods=['POST'])
def submit_post():
    data = request.json
    title = data['title']
    content = data['content']
    author_email = session.get('user_email')
    # print("Author email at post submission:", author_email) 
    post_id = posts_collection.insert_one({'title': title, 'content': content, 'author': author_email}).inserted_id
    return jsonify({'result': 'success', 'post_id': str(post_id), 'author_email': author_email})

@app.route('/clear-posts', methods=['POST'])
def clear_posts():
    try:
        posts_collection.delete_many({})
        replies_collection.delete_many({})
        return jsonify({'result': 'success'})
    except Exception as e:
        print(e)
        return jsonify({'result': 'error', 'message': str(e)}), 500

@app.route('/posts/<post_id>')
def post_detail(post_id):
    post_data = posts_collection.find_one({'_id': ObjectId(post_id)})
    if post_data:
        author_email = post_data.get('author', 'Unknown author')
        # print("Author email at post detail:", author_email)
        replies_data = replies_collection.find({'threadId': ObjectId(post_id)})
        replies = list(replies_data)
        for reply in replies:
            reply['timestamp'] = reply['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ')
        return render_template('reply.html', post=post_data, author=author_email, replies=replies)
    else:
        return "Post not found", 404


@app.route('/submit-reply', methods=['POST'])
def submit_reply():
    data = request.json
    thread_id = data['threadId']
    content = data['content']
    reply_id = replies_collection.insert_one({
        'threadId': ObjectId(thread_id),
        'content': content,
        'timestamp': datetime.utcnow()
    }).inserted_id

    if reply_id:
        return jsonify({'result': 'success', 'reply_id': str(reply_id)})
    else:
        return jsonify({'result': 'error', 'message': 'Failed to insert reply'}), 500
    
@app.route('/my_posts')
def my_posts():
    user_email = session.get('user_email', None) 
    if not user_email:
        flash('Please log in to see your posts.') 
        return redirect(url_for('login'))
    
    user_posts = list(posts_collection.find({'author': user_email}))

    for post in user_posts:
        content = post.get('content', '')
        post['content_preview'] = content.split('\n')[0] if content else ''
        
        if 'timestamp' in post:
            post['posting_time'] = post['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            post['posting_time'] = post['_id'].generation_time.strftime('%Y-%m-%dT%H:%M:%SZ') 
        
        last_reply = replies_collection.find_one(
            {'threadId': ObjectId(post['_id'])}, 
            sort=[('timestamp', pymongo.DESCENDING)]
        )
        if last_reply:
            post['last_reply_time'] = last_reply['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            post['last_reply_time'] = post['posting_time']
    return render_template('my_posts.html', posts=user_posts)



##################发帖子相关 function##################

@app.route('/message', methods=['GET', 'POST', 'PUT'])
def message():
    username = session.get('username', 'Guest') #default username = guest
    load_messages = list(chat_collection.find()) #load message from data base into list
    return render_template('message.html', username=username, messages = load_messages) #render message along with username to the update ones
    
@socketio.on("chat_message")
def user_input(message):
    sender = message["sender"]
    messages = message["message"]

    messages = messages.replace("&", "&amp")
    messages = messages.replace("<", "&lt")
    messages = messages.replace(">", "&gt")

    chat_collection.insert_one({"username": sender, "message": messages})
    emit("load_chat", {"username": sender, "message": messages},broadcast=True) #when load chat is broadcast can show allow other users to update their messages
    print(message)

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=8080)