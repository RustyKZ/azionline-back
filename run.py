from app import app, socketio
from OpenSSL import SSL
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('ssl/privkey.pem')
context.use_certificate_file('ssl/cert.pem')

# if __name__ == '__main__':
#     socketio.run(app, host='0.0.0.0', port=5000)

# if __name__ == '__main__':
#     app.run()
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)

# if __name__ == '__main__':
#     socketio.run(app, port=5000)

# if __name__ == '__main__':
#     socketio.run(app, host='0.0.0.0', port=5000, debug=True, ssl_context=context)

if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=80,
        debug=True,
        certfile='ssl/cert.pem',
        keyfile='ssl/privkey.pem',
        server_side=True)

# if __name__ == '__main__':
#     with app.app_context():
#         table_id = 1  # Замените на нужный вам ID стола
#         start_new_game(create_new_game(table_id))