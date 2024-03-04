from flask import Flask, request, render_template, send_from_directory

app = Flask(__name__)

@app.after_request
def security(response):
   response.headers['X-Content-Type-Options'] = 'nosniff'
   return response

@app.route('/', methods=['GET', 'POST'])
def login():
   if request.method == 'GET':

      return render_template('index.html')
def upload():
   if request.method == 'GET':
      return send_from_directory('static', 'design.png')

if __name__ == '__main__':
    app.run(debug=True)
