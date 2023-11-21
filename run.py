print('Hello World')
from app import app, socketio
from OpenSSL import SSL
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('ssl/privkey.pem')
context.use_certificate_file('ssl/cert.pem')
print('Hello World after import')

if __name__ == '__main__':
    print('AZI Started - inside if name == main')
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=False,
        certfile='ssl/cert.pem',
        keyfile='ssl/privkey.pem'
        )

# if __name__ == '__main__':
#     app.run()
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)
