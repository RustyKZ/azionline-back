from app import app, socketio, scheduler, weekly_scheduler, check_and_cleanup_tables, weekly_airdrop
from OpenSSL import SSL
context = SSL.Context(SSL.SSLv23_METHOD)
context.use_privatekey_file('ssl/privkey.pem')
context.use_certificate_file('ssl/cert.pem')

print('Before RUN Socket IO')

scheduler.add_job(check_and_cleanup_tables, 'interval', minutes=1)
scheduler.start()
weekly_scheduler.add_job(weekly_airdrop, 'interval', hours=1)
weekly_scheduler.start()

# if __name__ == '__main__':
#     app.run()
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)

# if __name__ == '__main__':
#     socketio.run(app, port=5000)

if __name__ == '__main__':
    print('Inside If=main')
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=False,
        certfile='ssl/cert.pem',
        keyfile='ssl/privkey.pem',
        server_side=True)
