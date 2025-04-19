from flask import Flask, request, jsonify

app = Flask(__name__)

# Manual CORS headers since flask_cors import may break compatibility
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the API"})

if __name__ == '__main__':
    # The following line has been removed for Render deployment
    # app.run(debug=True)
    pass  # Empty block to avoid IndentationError