import os
import datetime
import json

from flask import Flask, redirect, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
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
        if len(db.query(model.User).filter(model.User.username == data['username']).all()) == 1:
            return returns(0, {}, 'username already exists')
        else:
            db.add(
                model.User(username=data['username'],
                           email=data['email'],
                           password=data['password'],
                           imageUrl='http://127.0.0.1:5000/static/images/default.png',
                           createdTime=datetime.datetime.now()
                           )
            )
            db.commit()
            return returns(200, {}, 'success')
    else:
        return returns(1, {}, 'params lack')


@app.route("/user/login", methods=['post'])
def login():
    data = request.get_json()
    if data.__contains__('username') and data.__contains__('password'):
        user = db.query(model.User).filter(model.User.username == data['username']).all()
        if user[0].password == data['password']:
            return returns(200, {}, 'success')
        else:
            return returns(0, {}, 'password error')
    else:
        return returns(1, {}, 'params lack')


@app.route("/user/info", methods=['post'])
def user_info():
    data = request.get_json()
    if data.__contains__('username'):
        user = db.query(model.User).filter(model.User.username == data['username']).all()
        if len(user) == 1:
            return returns(200, {
                'username': user[0].username,
                'face_url': user[0].imageUrl
            }, 'success')
        else:
            return returns(0, {}, 'password error')
    else:
        return returns(1, {}, 'params lack')


@app.route('/upload/image', methods=['post'])
def upload_image():
    return ''


channel = ['chatroom1', 'chatroom2']
users = {}


@socket_io.on('connect')
def connect():
    emit('allChannel', channel)
    users.__setitem__(request.sid, channel[0])
    join_room(channel[0], sid=request.sid)
    print(users)


@socket_io.on('changeChannel')
def change_channel(data):
    leave_room(room=data['leftRoom'], sid=request.sid)
    join_room(room=data['room'], sid=request.sid)
    messages = db.query(model.Message).filter(model.Message.channel == data['room']).order_by(model.Message.createdTime.desc()).limit(100).all()
    users[request.sid] = data['room']
    msg = []
    for m in messages:
        msg.append(m.content)
    emit('changeChannelMessage', msg)


@socket_io.on('add_channel')
def add_channel(room):
    channel.append(room)
    emit('appendChannel', room, broadcast=True)


@socket_io.on('msg')
def msg(data):
    data.__setitem__('time', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(json.dumps(data))
    db.add(model.Message(content=json.dumps(data), createdTime=datetime.datetime.now(), channel=users[request.sid]))
    db.commit()
    emit('msg', data, room=users[request.sid])


@socket_io.on('disconnect')
def disconnect():
    users.__delitem__(request.sid)
    print('someone disconnect')


if __name__ == '__main__':
    socket_io.run(app)
