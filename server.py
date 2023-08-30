import asyncio

import google.auth.transport.requests

import os
import pathlib
import requests
import cachecontrol
from flask import Flask, render_template, request, session, abort, redirect
from flask import url_for

from flask import flash

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators

from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

server = Flask(__name__)

server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
server.config['SECRET_KEY'] = 'secret!'

bcrypt = Bcrypt(server)
db = SQLAlchemy()

socketio = SocketIO(server)

GOOGLE_CLIENT_ID = "296003114435-m71o9543p7rgvskvg61e2o0fn8ut5t3g.apps.googleusercontent.com"
server.secret_key = "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"

client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

#login manager
login_manager = LoginManager()
login_manager.init_app(server)

#db creation

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

db.init_app(server)

with server.app_context():
    db.create_all()

# Creates a user loader callback that returns the user object given an id
@login_manager.user_loader
def loader_user(user_id):
	return User.query.get(user_id)

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

@server.route('/auth', methods=['GET', 'POST'])
def mylogin():
    myform = LoginForm()
    if myform.validate_on_submit():
        user = User.query.filter_by(username=myform.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, myform.password.data):
                login_user(user)
                return redirect(url_for('index', user_id = current_user.id))
            else:
                flash('Invalid username or password', 'danger')

    return render_template('auth.html', form=myform)

@server.route('/mylogout', methods=['GET', 'POST'])
@login_required
def mylogout():
    logout_user()
    return redirect(url_for('auth'))

@server.route('/registration', methods=['GET', 'POST'])
def registration():
    myform = RegisterForm()

    if myform.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(myform.password.data).decode('utf-8')
        new_user = User(username=myform.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('mylogin'))

    return render_template('registration.html', form=myform)

#websocket

rooms = {}

def assign_room_for_player(username):
    # Check each room
    for room, players in rooms.items():
        # If there's a room with only one player, join that room
        if len(players) == 1:
            players.append(username)
            return room

    # If no room is found or all rooms are full, create a new room
    room_name = "room_" + str(len(rooms) + 1)
    rooms[room_name] = [username]
    return room_name

ready_players = set()


@socketio.on('message')
def handle_message(message):
    print('Received message:', message)
    socketio.emit('response', {'data': 'Hello, client!'})

connected_players = 0

@socketio.on('connect')
def handle_connect():
    global connected_players
    connected_players += 1
    print(f'Player connected. Total players: {connected_players}')

@socketio.on('disconnect')
def handle_disconnect():
    global connected_players
    connected_players -= 1
    print(f'Player disconnected. Total players: {connected_players}')

ready_players = set()  # To keep track of ready players

@socketio.on('player_ready')
def handle_player_ready():
    ready_players.add(request.sid)  # Add the player's session ID to the set

    if len(ready_players) == 2:  # Check if two players are ready
        emit('start_game', broadcast=True)  # Notify both players to start the game
        ready_players.clear()  # Reset for the next game


@socketio.on('join_room')
def handle_join_room(data):
    room = data['room']
    join_room(room)
    rooms[request.sid] = room  # Store the player's room
    emit('status', {'msg': session['username'] + ' has entered the room.'}, room=room)


@socketio.on('player_move')
def handle_player_move(data):
    move = data['move']
    room = find_room_of_player(request.sid)  # Assuming you have a function to find the room of a player
    emit('opponent_move', {'move': move}, room=room, include_self=False)

@socketio.on('leave_room')
def handle_leave_room(data):
    room = data['room']
    leave_room(room)
    if request.sid in player_rooms:
        del rooms[request.sid]
    emit('status', {'msg': session['username'] + ' has left the room.'}, room=room)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in rooms:
        del rooms[request.sid]
        global connected_players
        connected_players -= 1
        print(f'Player disconnected. Total players: {connected_players}')

def find_room_of_player(sid):
    return rooms.get(sid, None)



# @socketio.on('player_ready')
# def handle_player_ready():
#     global ready_players
#     ready_players += 1
#     if ready_players == 2:
#         emit('start_game', broadcast=True)


# @socketio.on('join_room')
# def handle_join_room(data):
#     room = data['room']
#     join_room(room)
#     emit('status', {'msg': session['username'] + ' has entered the room.'}, room=room)


# @socketio.on('player_move')
# def handle_player_move(data):
#     room = data['room']
#     move = data['move']
#     player = session['username']

#     if room not in rooms:
#         rooms[room] = {}

#     rooms[room][player] = move

#     if len(rooms[room]) == 2:  # Both players have made their move
#         player1, player2 = list(rooms[room].keys())
#         move1, move2 = rooms[room][player1], rooms[room][player2]
#         winner = determine_winner(move1, move2)
#         emit('game_result', {'winner': winner}, room=room)
#         del rooms[room]  # Clear the room data

# def determine_winner(move1, move2):
    # if move1 == move2:
    #     return "It's a tie!"
    # if (move1 == "rock" and move2 == "scissors") or (move1 == "scissors" and move2 == "paper") or (move1 == "paper" and move2 == "rock"):
    #     return "Player 1 wins!"
    # else:
    #     return "Player 2 wins!"


# @socketio.on('player_ready')
# def handle_player_ready(data):
#     player_id = data['player_id']  # Assuming you're sending player_id from the client
#     ready_players.add(player_id)

#     if len(ready_players) == 2:
#         emit('start_game', broadcast=True)  # Send to all clients
#         ready_players.clear()  # Reset for the next game

#GOOGLE login

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://localhost/callback"
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper

@server.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@server.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect('/index')


@server.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@server.route('/favicon.ico')
def favicon():
    return "", 404

@server.route('/')
def auth():
    myform = LoginForm()
    return render_template('auth.html', form=myform)


@server.route('/index')
@login_required
def index():
    return render_template('index.html',  user_id = current_user.id)


@server.route('/ready')
def ready():
    return render_template('ready.html')


if __name__ == '__main__':
    socketio.run(server, debug=True)