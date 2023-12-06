import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '..', 'db', 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# CLIENT_URL = 'https://localhost:8080'
SECRET_KEY = 'your_secret_key'




