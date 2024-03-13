from flask import Flask, request, render_template, send_from_directory

from flask_socketio import SocketIO
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
def message_html():
   return render_template('message.html')

@socketio.on("chat_message")
def user_input(message):
   chat_collection.insert_one({"username": "Unauthorized_guest", "message": message})
   print(message)

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=8080)
