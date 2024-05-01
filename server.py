
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, make_response
from flask_socketio import SocketIO, emit
from bson import ObjectId
from datetime import datetime
from util import database
import pymongo, bcrypt, os, secrets, hashlib, pytz, re

# posts_collection.delete_many({})

app = Flask(__name__)
app.secret_key = '4d56sad5a1c23xs'
socketio = SocketIO(app,cors_allowed_origins="*",transports=['websocket'])

@app.after_request
def security(response):
   response.headers['X-Content-Type-Options'] = 'nosniff'
   return response

@app.route('/')
def home():
    user_email = database.get_user_email(request)
    return render_template('index.html', user_email=user_email)

################## auth function start ##################
@app.route('/signup_page')
def signup_page():
    return render_template('register.html')

@app.route('/signup', methods=['POST'])
def signup():
    email = str(request.form['email'])
    password = str(request.form['password'])
    confirm_pass = str(request.form['password_confirm'])

    if '@' not in email or invalid_char(email):
        flash('This is not an email.', 'info')
        return redirect(url_for('signup_page'))
    
    if database.find_user(email): #check email exists
        flash('Email already existed.', 'info')
        return redirect(url_for('signup_page'))
    
    if invalid_password(password):
        flash('Invalid password.', 'info')
        return redirect(url_for('signup_page'))
        
    if password != confirm_pass: #password does not match
        flash('Passwords do not match.', 'info')
        return redirect(url_for('signup_page'))
        
    #success
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    user = {"email": email, "password": hashed_pw, 'id': database.get_id()}
    database.add_user(user)
    
    return redirect(url_for('login_page'))

@app.route('/login_page')
def login_page():
    return render_template('login.html')
    
@app.route('/login', methods=['POST'])
def login():
    email = str(request.form['email'])
    password = str(request.form['password'])

    if database.valid_login(email, password):
        token = secrets.token_urlsafe()
        hashed_token = hashlib.sha256(token.encode()).hexdigest()
        database.update_user_doc({"email": email}, {"token": hashed_token})
        response = make_response(redirect(url_for('home')))
        response.set_cookie('auth_token', token, max_age = 3600, httponly = True, secure=True)
        return response
    
    flash('Login failed.', 'info')   
    return redirect(url_for('login_page')) #login failed

@app.route('/logout')
def logout():
    database.delete_token(request)
    response = make_response(redirect(url_for('login_page')))
    response.set_cookie('auth_token', "", expires = 0, httponly = True, secure=True)
    return response

def invalid_char(entry: str):
    # does not contain any invalid characters
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&()-_=.")
    if set(entry) - allowed_chars != set():
        return True
    return False

def invalid_password(password: str):
    if len(password) < 8:
        return True
    
    # at least 1 lowercase letter
    if re.search("[a-z]", password) == None:
        return True
    
    # at least 1 uppercase letter
    if re.search("[A-Z]", password) == None:
        return True
    
    # at least 1 number
    if  re.search("[0-9]", password) == None:
        return True
    
################## post function start ##################
@app.route('/explore')
def posts_list_html():
    user_email = database.get_user_email(request)
    if user_email == 'Guest':
        return redirect(url_for('login_page'))
    
    all_posts = database.get_all_post()
    for post in all_posts:
        content = post.get('content', '')
        post['content_preview'] = content.split('\n')[0] if content else ''
        
        if 'timestamp' in post:
            post['posting_time'] = post['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            post['posting_time'] = post['_id'].generation_time.strftime('%Y-%m-%dT%H:%M:%SZ') 
        
        last_reply = database.replies_collection.find_one(
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
    author_email = database.get_user_email(request)

    title = title.replace("&amp;","&")
    title = title.replace("&lt;","<")
    title = title.replace("&gt;",">")

    content = content.replace("&amp;","&")
    content = content.replace("&lt;","<")
    content = content.replace("&gt;",">")

    # print("Author email at post submission:", author_email) 
    post_id = database.posts_collection.insert_one({'title': str(title), 'content': str(content), 'author': author_email}).inserted_id
    return jsonify({'result': 'success', 'post_id': str(post_id), 'author_email': author_email})

@app.route('/delete-post/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    try:
        user_email = database.get_user_email(request)
        post_data = database.posts_collection.find_one({'_id': ObjectId(post_id), 'author': user_email})
        if not post_data:
            return jsonify({'status': 'error', 'message': 'Post not found or user unauthorized'}), 404
        database.posts_collection.delete_one({'_id': ObjectId(post_id)})
        database.replies_collection.delete_many({'threadId': ObjectId(post_id)})
        return jsonify({'status': 'success', 'message': 'Post deleted successfully'})
    except Exception as e:
        print(e)
        return jsonify({'status': 'error', 'message': 'Failed to delete post'}), 500

@app.route('/clear-posts', methods=['POST'])
def clear_posts():
    try:
        database.posts_collection.delete_many({})
        database.replies_collection.delete_many({})
        return jsonify({'result': 'success'})
    except Exception as e:
        print(e)
        return jsonify({'result': 'error', 'message': str(e)}), 500

@app.route('/posts/<post_id>')
def post_detail(post_id):
    post_data = database.posts_collection.find_one({'_id': ObjectId(post_id)})
    if post_data:
        author_email = post_data.get('author', 'Unknown author')
        replies_data = database.replies_collection.find({'threadId': ObjectId(post_id)})
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
    author_email = database.get_user_email(request)

    content = content.replace("&amp;","&")
    content = content.replace("&lt;","<")
    content = content.replace("&gt;",">")

    reply_id = database.replies_collection.insert_one({
        'threadId': ObjectId(thread_id),
        'content': str(content),
        'timestamp': datetime.now(pytz.timezone('UTC')),
        'author': author_email
    }).inserted_id

    if reply_id:
        return jsonify({'result': 'success', 'reply_id': str(reply_id), 'author_email': author_email})
    else:
        return jsonify({'result': 'error', 'message': 'Failed to insert reply'}), 500

@app.route('/my_posts')
def my_posts():
    user_email = database.get_user_email(request)
    if user_email == 'Guest':
        return redirect(url_for('login_page'))
    
    user_posts = list(database.posts_collection.find({'author': user_email}))

    for post in user_posts:
        content = post.get('content', '')
        post['content_preview'] = content.split('\n')[0] if content else ''
        
        if 'timestamp' in post:
            post['posting_time'] = post['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            post['posting_time'] = post['_id'].generation_time.strftime('%Y-%m-%dT%H:%M:%SZ') 
        
        last_reply = database.replies_collection.find_one(
            {'threadId': ObjectId(post['_id'])}, 
            sort=[('timestamp', pymongo.DESCENDING)]
        )
        if last_reply:
            post['last_reply_time'] = last_reply['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            post['last_reply_time'] = post['posting_time']
    return render_template('my_posts.html', posts=user_posts)

@app.route('/search', methods=['GET'])
def search():
    search_result = request.args.get('search', '')
    search_result = search_result.replace("&amp;","&")
    search_result = search_result.replace("&lt;","<")
    search_result = search_result.replace("&gt;",">")

    if search_result != '' and search_result != None:

        regex = {'$regex': search_result, '$options': 'i'}
        search_results = list(database.get_all_post_raw().find({'title': regex}))

        for post in search_results:
            content = post.get('content', '')
            post['content_preview'] = content.split('\n')[0] if content else ''
            
            if 'timestamp' in post:
                post['posting_time'] = post['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ')
            else:
                post['posting_time'] = post['_id'].generation_time.strftime('%Y-%m-%dT%H:%M:%SZ') 
            
            last_reply = database.replies_collection.find_one(
                {'threadId': ObjectId(post['_id'])}, 
                sort=[('timestamp', pymongo.DESCENDING)]
            )
            if last_reply:
                post['last_reply_time'] = last_reply['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ')
            else:
                post['last_reply_time'] = post['posting_time']
            
        return render_template('post.html', posts=search_results)
    else: 
        return redirect("/explore")
    
##################posting function##################

@app.route('/message', strict_slashes=False, methods=['GET', 'POST', 'PUT'])
def message():
    username = database.get_user_email(request)
    if username == 'Guest':
        return redirect(url_for('login_page'))
    
    user_doc = database.find_user(username)

    load_messages = list(database.chat_collection.find())
    for message in load_messages:
        user_doc = database.cred_collection.find_one({'id': message['user_id']})
        message['username'] = user_doc.get('new_username', user_doc['email'])
        message['profile_pic'] = user_doc.get('photo_path', './static/profile_images/default.png').replace('./','/')


    return render_template('message.html', username=username, messages = load_messages) #render message along with username to the update ones
    
@socketio.on("chat_message")
def user_input(message):
    username = database.get_user_email(request)
    user_doc = database.find_user(username)
    user_id = user_doc.get('id')
    current_avatar_path = user_doc.get('photo_path', './static/profile_images/default.png').replace('./', '/')

    sender = message["sender"]
    messages = (message["message"])
    database.chat_collection.insert_one({"user_id": user_id,"message": messages})
    emit("load_chat", {"username": sender, "message": messages,"profile_pic": current_avatar_path},broadcast=True) #when load chat is broadcast can show allow other users to update their messages
    print(message)
################## message function end ##################

@app.route('/profile', methods=['POST','GET'])
def profile():
    user_email = database.get_user_email(request)
    if user_email == 'Guest':
        return redirect(url_for('login_page'))
    
    doc = database.find_user(user_email)
    
    get_photo_path = "./static/profile_images/default.png"
    if request.method == "GET":
        if 'photo_path' in doc:
            get_photo_path = doc['photo_path']
            
        if 'new_username' in doc:
            user_email = doc['new_username']

        return render_template('profile.html',user_email=user_email, get_photo_path=get_photo_path)
    
    elif request.method == "POST":
        if 'uploaded_pic' in request.files:
            photo = request.files['uploaded_pic']
            photo_header = photo.read(64)
            photo.seek(0)
            pnghex = "89504E470D0A1A0A"
            png = bytes.fromhex(pnghex)

            im_type = ''
            if photo_header.startswith(b'\xFF\xD8'): #jpeg&jpg
                im_type = '.jpeg'
            elif photo_header.startswith(png): #png
                im_type = '.png'

            filename = 'profile_pic_'+str(doc['id'])+im_type
            path = os.path.join('./static/profile_images',filename)
            photo.save(path)
            database.update_user_doc({"email":user_email}, {'photo_path': path})

            return redirect(url_for('profile'))
        
        elif 'username' in request.form:
            new_name = request.form.get('username')
            database.update_user_doc({"email":user_email}, {'new_username': new_name})        
            return redirect(url_for('profile'))

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=8080)
