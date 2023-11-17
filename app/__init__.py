from flask import Flask
from app.db import db
from app.classes import *
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from web3 import Web3
from flask_socketio import SocketIO
# from app.config import CLIENT_URL
from apscheduler.schedulers.background import BackgroundScheduler
import time
from flask_migrate import Migrate

app = Flask(__name__)
jwt = JWTManager(app)
CORS(app)
# socketio = SocketIO(app, cors_allowed_origins=CLIENT_URL)
CORS(app, resources={r"/*": {"origins": ["http://azi-online.com", "https://azi-online.com", "http://127.0.0.1", "https://127.0.0.1"]}})
# CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins=["http://azi-online.com", "https://azi-online.com", "http://127.0.0.1", "htts://127.0.0.1"])
# socketio = SocketIO(app, cors_allowed_origins="*")

# socketio = SocketIO(app)
scheduler = BackgroundScheduler()
weekly_scheduler = BackgroundScheduler()

from app.sockets import *

bsc_rpc_url = "https://bsc-dataseed.binance.org/"
w3 = Web3(Web3.HTTPProvider(bsc_rpc_url))

bcrypt = Bcrypt()

app.config.from_pyfile('config.py')
db.init_app(app)
# migrate = Migrate(app, db)

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=12)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Получение текущих настроек токена
access_token_expires = app.config.get('JWT_ACCESS_TOKEN_EXPIRES')
refresh_token_expires = app.config.get('JWT_REFRESH_TOKEN_EXPIRES')

print(f"Срок действия токена: {access_token_expires}")
print(f"Время неактивности токена: {refresh_token_expires}")

from app import routes

def check_and_cleanup_tables():
    print('Scheduler is running...')
    with app.app_context():
        try:
            tables = Tables.query.all()
            for table in tables:
                if table.time_stop != 0:
                    current_time = int(time.time())
                    if ((current_time - table.time_stop) > 180) and (table.players_now < 1):
                        db.session.delete(table)
                        db.session.commit()
                        socketio.emit('update_tables', to='tables')
        except Exception as e:
            print(f"An error occurred: {e}")

def weekly_airdrop():
    current_day = datetime.utcnow().weekday()  # 0 is Monday, 6 is Sunday
    if current_day != 0:  # Check if today is Monday
        return
    last_airdrop = Weekly.query.order_by(Weekly.date.desc()).first()
    if last_airdrop and (datetime.utcnow() - last_airdrop.date).days < 6:
        return  # Airdrop already conducted within the last 6 days
    # Your airdrop mechanism goes here
    try:
        total_airdrop = 0
        users = Players.query.all()
        for user in users:
            user.freecoin += 1000
            user.airdopfree += 1000
            total_airdrop =+ 1000
        # Create a new record in the Weekly table
        new_airdrop = Weekly(total_freecoin = total_airdrop)
        db.session.add(new_airdrop)
        db.session.commit()
    except:
        return

weekly_scheduler.add_job(weekly_airdrop, 'interval', hours=1)
scheduler.add_job(check_and_cleanup_tables, 'interval', minutes=1)
scheduler.start()
weekly_scheduler.start()

# with app.app_context():
#     db.create_all()
