from flask import Flask, request, render_template, send_from_directory, jsonify


app = Flask(__name__)

@app.after_request
def security(response):
   response.headers['X-Content-Type-Options'] = 'nosniff'
   return response

@app.route('/')
def home():
   return render_template('index.html')


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
