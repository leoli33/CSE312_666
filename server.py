from flask import Flask, request, render_template, send_from_directory

app = Flask(__name__)

@app.after_request
def security(response):
   response.headers['X-Content-Type-Options'] = 'nosniff'
   return response

@app.route('/')
def home():
   return render_template('index.html')

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=8080)
