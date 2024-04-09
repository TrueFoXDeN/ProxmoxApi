from flask import Flask
from flask_cors import CORS

from api.auth import encode_token
from api.exceptions import exception_handler
from api import response_generator as r

app = Flask(__name__)
cors = CORS(app)


@app.route('/', methods=["GET"])
@exception_handler("index")
def index():
    return r.respond({'hello': 'hello'})


@app.route('/token/admin', methods=["GET"])
@exception_handler("token admin")
def token_admin():
    token = encode_token({'uid': 'admin'})
    return r.respond({"token": token}, cookie=f"Authorization={token}")


@app.route('/token/user', methods=["GET"])
@exception_handler("token admin")
def token_user():
    token = encode_token({'uid': 'user'})
    return r.respond({"token": token}, cookie=f"Authorization={token}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
