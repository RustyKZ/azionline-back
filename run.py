from app import app, socketio

# if __name__ == '__main__':
#     socketio.run(app, host='0.0.0.0', port=8000)

if __name__ == '__main__':
    app.run()

# if __name__ == '__main__':
#     socketio.run(app, host='0.0.0.0', port=8000, debug=True, allow_unsafe_werkzeug=True)



# from app import app
#
# if __name__ == '__main__':
#     app.run(debug=True, port=8000)

# if __name__ == '__main__':
#     with app.app_context():
#         table_id = 1  # Замените на нужный вам ID стола
#         start_new_game(create_new_game(table_id))