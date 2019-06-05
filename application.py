import os
import datetime

from flask import Flask, redirect, request, jsonify
from flask_socketio import SocketIO, emit
import model

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socket_io = SocketIO(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
db = model.create(os.getenv("DATABASE_URL")).session_factory()


def returns(code, data, msg):
    return jsonify({'code': code, 'data': data, 'msg': msg})


@app.route("/")
def index():
    return redirect('/static/index.html')


@app.route("/user/signup", methods=['post'])
def signup():
    data = request.get_json()
    if data.__contains__('username') and data.__contains__('email') and data.__contains__('password'):
        if len(db.query(model.User).filter(model.User.username == data['username'])) == 1:
            return returns(0, {}, 'username already exists')
        else:
            db.add(model.User(username=data['username'], email=data['email'], password=data['password'], createdTime=datetime.datetime.now()))
            db.commit()
            return returns(200, {}, 'success')
    else:
        return returns(1, {}, 'params lack')


@app.route("/user/login", methods=['post'])
def login():
    data = request.get_json()
    if data.__contains__('username') and data.__contains__('password'):
        user = db.query(model.User).filter(model.User.username == data['username']);
        if user.password == data['password']:
            return returns(200, {}, 'success')
        else:
            return returns(0, {}, 'password error')
    else:
        return returns(1, {}, 'params lack')