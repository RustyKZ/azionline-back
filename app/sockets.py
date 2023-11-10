# Импортируйте экземпляр socketio из вашего приложения Flask
from app import socketio
from flask_socketio import join_room, leave_room

@socketio.on('connect')
def handle_connect():
    print('Socket.IO CONNECTED')

@socketio.on('disconnect')
def test_disconnect():
    print('Socket.IO DISCONNECTED')

@socketio.on('join_room')
def handle_join_room(data):
    room_id = data['room_id']
    join_room(room_id)
    user_id = data['user_id']
    print('Socket.on JOIN ROOM: User ', user_id, f" joined room: {room_id}")
    # socketio.emit('update_tables', data, to=room_id)

@socketio.on('leave_room')
def handle_leave_room(data):
    room_id = data['room_id']
    leave_room(room_id)
    user_id = data['user_id']
    print('Socket.on LEAVE ROOM: User ', user_id, f" left room: {room_id}")
    # socketio.emit('update_tables', data, to=room_id)

@socketio.on('update_tables_hall')
def handle_update_tables_hall():
    print('Socket.on UPDATE_TABLES_HALL: room = tables')
    socketio.emit('update_tables', to='tables')

@socketio.on('update_room')
def handle_update_room(data):
    room_id = data['room_id']
    user_id = data['user_id']
    print('Socket.on UPDATE ROOM: User ', user_id, f" updated room: {room_id}")
    socketio.emit('update_room', data, to=room_id)
