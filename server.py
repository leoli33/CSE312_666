from flask import Flask, request, render_template, send_from_directory, session

from flask_socketio import SocketIO, emit
from pymongo import MongoClient

mongo_client = MongoClient("mongo")
db = mongo_client["CSE312_666"]
chat_collection = db["Chat_room"]

app = Flask(__name__)
socketio = SocketIO(app)

@app.after_request
def security(response):
   response.headers['X-Content-Type-Options'] = 'nosniff'
   return response

@app.route('/')
def index_html():
   return render_template('index.html')

@app.route('/home')
def home_html():
    return render_template('home.html')

@app.route('/post')
def post_html():
    return render_template('post.html')

@app.route('/message', methods=['GET', 'POST', 'PUT'])
def message():
    username = session.get('username', 'Guest')
    return render_template('message.html', username=username)
    
@socketio.on("chat_message")
def user_input(message):
    sender = message["sender"]
    messages = message["message"]

    messages = messages.replace("&", "&amp")
    messages = messages.replace("<", "&lt")
    messages = messages.replace(">", "&gt")

    chat_collection.insert_one({"username": sender, "message": messages})
    emit("load_chat", {"username": sender, "message": messages},broadcast=True)
    print(message)

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=8080)
