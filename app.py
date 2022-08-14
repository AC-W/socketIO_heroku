import socketio
import chess
from database import DataBase as db
sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

myDataBase = db()

# each entry in games:
# {gameID(string):
#   {
#       'game': game(object),
#       'users': set({userIds...}),
#       'white_player_id':userid1,
#       'black_player_id':userid2,
#       'numberofusers':0,
#       'chat':""
#    }
# }
# if white_player_id and black_player_id not in users free game object and clear database entry
# when new player_id post start_game add it to the users
# To do:
#   if white_player or black_player id not set return prompt to select player color
games = {}
game = chess.Board()

# each entry in users:
# { userID(string):
#   {
#       'username':username(string)
#       'gameID': gameID(string)
#   }
#   
# }
users = {}

client_count = 0

# helper functions:
def fen_to_array(fen):
    board = fen.split(' ')[0]
    board = board.split('/')
    array = []
    for i in board:
        row = []
        for x in i:
            try:
                x = int(x)
                for y in range(x):
                    row.append('.')
            except:
                row.append(x)
        array.append(row)
    return array
def quitRoom(client):
    if 'game' in users[client]:
        name = users[client]['username']
        games[users[client]['game']]['chat'] += f'{name} has left the room\n\n'
        games[users[client]['game']]['users'].remove(client)
        if  games[users[client]['game']]['white_player_ID'] == client:
            games[users[client]['game']]['white_player_ID'] = 'nothing'
        if  games[users[client]['game']]['black_player_ID'] == client:
            games[users[client]['game']]['black_player_ID'] = 'nothing'
        chat = games[users[client]['game']]['chat']
        sio.emit('update_chat',{'chat': chat},to=users[client]['game'])

        if len(games[users[client]['game']]['users']) == 0:
            games.pop(users[client]['game'])
        users[client].pop('game')

# Server Connection/Disconnection
@sio.event
def connect(client,environ):
    global client_count
    client_count += 1
    print(client,'connected')
    new_user = {client:
                    {
                        'username':'guest-'+client[0:5],
                    }
                }
    users.update(new_user)
    sio.emit('new client',{'client_ID':client},to=client)

@sio.event
def disconnect(client):
    global client_count
    client_count -= 1
    print(client,'disconnected')
    if client in users:
        print("logging_off")
        print(client)
        quitRoom(client)
        users.pop(client)
        print(games)
        print(users)
    else:
        print("logging_off error (userId not found)")
        print(games)
        print(users)

@sio.event
def get_server_status(client):
    sio.emit('server_status',{'client_count':client_count},to=client)

@sio.event
def server_reset():
    global client_count
    users.clear()
    games.clear()
    client_count = 0

# User login:
@sio.event
def login(client,data):
    user_ID = data['user_ID']
    password = data['password']
    user_info = myDataBase.retrive_user_Info(user_ID,password)
    if user_info:
        print(user_info)
        new_user = {client:
                    {
                        'username':user_info[1],
                    }
                }
        users.update(new_user)
        # [0] : user_ID
        # [1] : username
        # [2] : password
        sio.emit('success',{'msg':'Logged in'},to=client)
        sio.emit('logged in',{'user_ID':user_info[0],'username':user_info[1],'password':user_info[2]},to=client)
    else:
        sio.emit('error',{'msg':'Login failed'},to=client)

# User log off:
@sio.event
def log_off(client):
    if client in users:
        print("logging_off")
        print(client)
        quitRoom(client)
        users.pop(client)
        sio.emit('success',{'msg':'Logged out'},to=client)
    else:
        sio.emit('error',{'msg':'failure to log out'},to=client)
        print("logging_off error (userId not found)")

# Account Creation:
@sio.event
def create_account(client,data):
    if myDataBase.check_user_exists('Users',data['new_user_ID']):
        sio.emit('error',{'msg':'User already exists'},to=client)
    else:
        add_user = (f"INSERT INTO Users (id, username, password) VALUES ('{data['new_user_ID']}','{data['new_username']}','{data['password']}')")
        myDataBase.exercute_raw_SQL(add_user)
        sio.emit('account_creation_success',to=client)
        sio.emit('success',{'msg':'Account created'},to=client)

# Joinning Rooms:
@sio.event
def join_game(client,data):
    gameID = data['game_ID']
    join_as = data['join_as']
    if client not in users:
        new_user = {client:
            {
                'username':'guest-'+client[0:5],
            }
        }
        users.update(new_user)

    # Quit old room
    quitRoom(client)
        
    # if game room does not exist create one
    new_room = False
    if gameID not in games:
        new_room = True
        game = chess.Board()
        new_game = {gameID:
            {
                'game':game,
                'users':set({}),
                'white_player_ID':'nothing',
                'black_player_ID':'nothing',
                'numberofusers': 0,
                'chat':"",
            }
        }
        games.update(new_game)
    
    # check if client can play as the desired roles
    if join_as == 'white' and games[gameID]['white_player_ID'] == 'nothing':
            games[gameID]['white_player_ID'] = client
    elif join_as == 'black' and games[gameID]['black_player_ID'] == 'nothing':
            games[gameID]['black_player_ID'] = client
    elif join_as == 'spectate':
        pass
    else:
        if new_room:
            games.pop(gameID)
        sio.emit('error',{'msg':'failure to join'},to=client)
        return

    # update server status
    games[gameID]['users'].add(client)
    users[client].update({'game':gameID})
    games[gameID]['numberofusers'] += 1
    sio.enter_room(client,gameID)
    name = users[client]['username']
    games[gameID]['chat'] += f'{name} has joined the room as {join_as}\n\n'
    
    # return the updated state to the gameroom
    game_array = fen_to_array(games[gameID]['game'].fen())
    whiteplayer = games[gameID]['white_player_ID']
    blackplayer = games[gameID]['black_player_ID']
    number = games[gameID]['numberofusers']
    chat = games[gameID]['chat']
    print(games)
    print(users)

    # sio.emit('update_state',
    #     {'game_array':game_array,
    #     'whiteplayer':whiteplayer,
    #     'blackplayer':blackplayer,
    #     'numberofplayers':number,
    #     'chat': chat
    #     },
    # to=gameID)

    sio.emit('update_board',{'game_array':game_array},to=client)
    sio.emit('joined as',{'join_as':join_as},to=client)
    sio.emit('update_chat',{'chat': chat},to=gameID)
    sio.emit('success',{'msg':'Joined Game'},to=client)

# Room chat:
@sio.event
def new_message(client,data):
    gameID = data['game_ID']
    message = data['message']
    username = users[client]['username']
    games[gameID]['chat'] += f'{username}:\n{message}\n\n'
    chat = games[gameID]['chat']
    sio.emit('update_chat',{'chat': chat},to=gameID)

# Moves on board:
@sio.event
def check_move_piece(client,data):
    gameID = data['game_ID']
    uci = data['uci']
    array = list(games[gameID]['game'].legal_moves)
    validmove = []
    for i in array:
        i = str(i)
        if uci[0] == i[0] and uci[1] == i[1]:
            validmove.append(i)
    sio.emit('update_move_check',{'validmove':validmove},to=client)

@sio.event
def check_move(client,data):
    gameID = data['game_ID']
    uci = data['uci']
    game_array = fen_to_array(games[gameID]['game'].fen())
    if chess.Move.from_uci(uci) in games[gameID]['game'].legal_moves:
        games[gameID]['game'].push_uci(uci)
        print(games[gameID]['game'])
        game_array = fen_to_array(games[gameID]['game'].fen())
        sio.emit('update_board',{'game_array':game_array},to=gameID)
    else:
        sio.emit('error',{'msg':'invalid move'},to=client)
        print("invalid move")

# Local (windows) machine debug: -->
# import eventlet
# import eventlet.wsgi
# import logging
# requests_log = logging.getLogger("socketio")
# requests_log.setLevel(logging.ERROR)
# eventlet.wsgi.server(eventlet.listen(('', 5000)), app,log=requests_log)
# Local (windows) machine debug: <--