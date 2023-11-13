from app import app, socketio

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)

# if __name__ == '__main__':
#     app.run()

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)

# if __name__ == '__main__':
#     socketio.run(app, port=5000)

# if __name__ == '__main__':
#     with app.app_context():
#         table_id = 1  # Замените на нужный вам ID стола
#         start_new_game(create_new_game(table_id))
