import socketio

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid,environ):
    print(sid,'connected')
    pass

@sio.event
def disconnect(sid):
    print(sid,'disconnected')
    pass