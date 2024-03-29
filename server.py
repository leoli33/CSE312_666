
from flask import Flask, request, render_template, send_from_directory, jsonify, redirect, url_for, flash, make_response
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import pymongo, bcrypt, string, random

mongo_client = MongoClient("mongo")
db = mongo_client["CSE312_666"]
chat_collection = db["Chat_room"]
posts_collection = db["Posts"]
replies_collection = db['Replies']
cred_collection = db["cred"]

app = Flask(__name__)
socketio = SocketIO(app)

def get_username():
    auth_cook = request.cookies.get('auth_token')

    if auth_cook != None and auth_cook != "":
        for doc in cred_collection.find({},{'_id' : False}):

            if "auth_token" in doc.keys() and doc["auth_token"] != '' and bcrypt.checkpw(auth_cook.encode(),doc["auth_token"]):
                return doc["email"]
    return 'Guest'
    
@app.after_request
def security(response):
   response.headers['X-Content-Type-Options'] = 'nosniff'
   return response

@app.route('/')
def home():
    user_email = get_username()
    return render_template('index.html', user_email=user_email)

@app.route('/signup_page')
def signup_page():
     return render_template('register.html')

@app.route('/signup', methods=['POST'])
def signup():

    if request.method == 'POST':

        email = str(request.form['email'])
        password = str(request.form['password'])
        confirm_pass = str(request.form['password_confirm'])


        if cred_collection.find_one({'email': email}) or email == 'Guest': #check email exists
          
            return render_template('register.html')
        else:

            if password != confirm_pass: #password does not match
                return render_template('register.html')
            
            else: #success
                hashed_pass = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                cred_collection.insert_one({"email":email,"password":hashed_pass})
                return redirect(url_for('login_page'))
        
@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':

        email = str(request.form['email'])
        password = str(request.form['password'])

        for doc in cred_collection.find({},{'_id' : False}):

            if email == doc["email"] and bcrypt.checkpw(password.encode(),doc["password"]): #can log in

                N = 20
                auth_tok = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=N))
                hashed_token = bcrypt.hashpw(auth_tok.encode(), bcrypt.gensalt())

                cred_collection.update_one({"email":doc["email"], "password":doc["password"]}, {"$set":{"email" : doc["email"],  "password" : doc["password"], "auth_token": hashed_token}})

                response = make_response(redirect(url_for('home')))
                response.set_cookie('auth_token', auth_tok, max_age = 3600, httponly = True)
                return response
            
        return redirect(url_for('login_page')) #login failed

@app.route('/logout',methods = ['POST','GET'])
def logout():
    if request.method == "GET":

        auth_cook = request.cookies.get('auth_token')

        for doc in cred_collection.find({},{'_id' : False}):

            if "auth_token" in doc.keys() and doc["auth_token"] != '' and bcrypt.checkpw(auth_cook.encode(),doc["auth_token"]):

                cred_collection.update_one({"email":doc["email"] ,"password":doc["password"],"auth_token":doc["auth_token"]}, {"$set":{"email" : doc["email"],  "password" : doc["password"], "auth_token": ""}})
                response = make_response(redirect(url_for('home')))
                response.set_cookie('auth_token', "", expires = 0, httponly = True)
                return response

##################发帖子相关 function##################
@app.route('/explore')
def posts_list_html():
    user_email = get_username()
    if user_email == 'Guest':
        return redirect(url_for('login_page'))
    
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
    author_email = get_username()

    title = title.replace("&amp;","&")
    title = title.replace("&lt;","<")
    title = title.replace("&gt;",">")

    content = content.replace("&amp;","&")
    content = content.replace("&lt;","<")
    content = content.replace("&gt;",">")

    # print("Author email at post submission:", author_email) 
    post_id = posts_collection.insert_one({'title': str(title), 'content': str(content), 'author': author_email}).inserted_id
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
        replies_data = replies_collection.find({'threadId': ObjectId(post_id)})
        replies = []
        for reply in replies_data:
            # Add author_email or username to reply object
            reply['author'] = reply.get('author', 'Unknown author')
            reply['timestamp'] = reply['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ')
            replies.append(reply)
        return render_template('reply.html', post=post_data, author=author_email, replies=replies)
    else:
        return "Post not found", 404



@app.route('/submit-reply', methods=['POST'])
def submit_reply():
    data = request.json
    thread_id = data['threadId']
    content = data['content']
    author_email = get_username()

    content = content.replace("&amp;","&")
    content = content.replace("&lt;","<")
    content = content.replace("&gt;",">")

    reply_id = replies_collection.insert_one({
        'threadId': ObjectId(thread_id),
        'content': str(content),
        'timestamp': datetime.utcnow(),
        'author': author_email
    }).inserted_id

    if reply_id:
        return jsonify({'result': 'success', 'reply_id': str(reply_id), 'author_email': author_email})
    else:
        return jsonify({'result': 'error', 'message': 'Failed to insert reply'}), 500

    
@app.route('/my_posts')
def my_posts():
    user_email = get_username()
    if user_email == 'Guest':
        return redirect(url_for('login_page'))
    
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


##################posting unction##################

@app.route('/message', methods=['GET', 'POST', 'PUT'])
def message():
    username = get_username()
    if username == 'Guest':
        return redirect(url_for('login_page'))
    
    load_messages = list(chat_collection.find()) #load message from data base into list
    return render_template('message.html', username=username, messages = load_messages) #render message along with username to the update ones
    
@socketio.on("chat_message")
def user_input(message):
    sender = message["sender"]
    messages = (message["message"])
    chat_collection.insert_one({"username": sender, "message": messages})
    emit("load_chat", {"username": sender, "message": messages},broadcast=True) #when load chat is broadcast can show allow other users to update their messages
    print(message)

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=8080)
