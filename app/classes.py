from datetime import datetime
from app import db  # Поменяйте на вашу переменную db для SQLite
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean

class Articles(db.Model):
    __tablename__ = 'website'
    id = Column(Integer, primary_key=True)
    Title = Column(String(256))
    SubTitle = Column(Text)
    Text = Column(Text)
    PublicationDate = Column(DateTime, default=datetime.utcnow)
    Image = Column(String(256))

    def __repr__(self):
        return '<Articles %r>' % self.id

class Rules(db.Model):
    __tablename__ = 'rules'
    id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(256))
    SubTitle = db.Column(db.Text)
    Text = db.Column(db.Text)
    Image = db.Column(db.String(256))

    def __repr__(self):
        return '<Rules %r>' % self.id

class About(db.Model):
    __tablename__ = 'about'
    id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(256))
    SubTitle = db.Column(db.Text)
    Text = db.Column(db.Text)
    Image = db.Column(db.String(256))

    def __repr__(self):
        return '<Rules %r>' % self.id

# Описание класса пользователей
class Players(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(255))
    password = db.Column(db.String(255))
    email = db.Column(db.String(255))
    freecoin = db.Column(db.Integer, default=1000)
    goldcoin = db.Column(db.Integer)
    ip_address = db.Column(db.String(255))
    reg_date = db.Column(db.DateTime, default=datetime.utcnow)
    active_table = db.Column(db.Integer, default=0)
    reputation = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    wallet = db.Column(db.String(255))
    game_status = db.Column(db.Integer, default=0)
    public_key = db.Column(db.String(255))
    airdropfree = db.Column(db.Integer, default=1000)
    airdropgold = db.Column(db.Integer, default=0)
    depositfree = db.Column(db.Integer, default=0)
    depositgold = db.Column(db.Integer, default=0)
    def __repr__(self):
        return '<Players %r>' % self.id

class Transactions(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer)
    freecoin = db.Column(db.Integer)
    goldcoin = db.Column(db.Integer)
    def __repr__(self):
        return '<Transactions %r>' % self.id

class Weekly(db.Model):
    __tablename__ = 'weekly'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    total_freecoin = db.Column(db.Integer)
    total_goldcoin = db.Column(db.Integer)
    def __repr__(self):
        return '<Weekly %r>' % self.id


# Описание класса игровых столов
class Tables(db.Model):
    __tablename__ = 'tables'
    id = db.Column(db.Integer, primary_key=True)
    max_players = db.Column(db.Integer)
    drop_suit = db.Column(db.Integer)
    cointype = db.Column(db.Integer)
    min_bet = db.Column(db.Integer)
    max_bet = db.Column(db.Integer)
    table_password = db.Column(db.String(255))
    players = db.Column(db.String(255), default='0, 0, 0, 0, 0, 0')
    blind_game = db.Column(db.Boolean)
    dealing = db.Column(db.Integer, default=1)
    currentgame = db.Column(db.Integer, default=0)
    players_now = db.Column(db.Integer, default=0)
    sort_index = db.Column(db.Integer, default=0)
    time_stop = db.Column(db.Integer, default=0)
    interval = db.Column(db.Integer)

    def __repr__(self):
        return '<Tables %r>' % self.id

# Описание класса игр
class Games(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    start_game = db.Column(db.DateTime, default=datetime.utcnow)
    table_id = db.Column(db.Integer)
    players = db.Column(db.String(255), default='0, 0, 0, 0, 0, 0')
    min_bet = db.Column(db.Integer)
    drop_suit = db.Column(db.Integer)
    trump_suit = db.Column(db.Integer, default=0)
    pot = db.Column(db.Integer, default=0)
    betting = db.Column(db.Text)
    gaming = db.Column(db.Text)
    end_game = db.Column(db.DateTime, default=None)
    winner = db.Column(db.Integer, default=0)
    lastgame = db.Column(db.Integer)
    card_deck = db.Column(db.String(255), default='1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1')
    card_players = db.Column(db.String(255), default='0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0')
    card_place1 = db.Column(db.String(255), default='0, 0, 0, 0, 0, 0')
    card_place2 = db.Column(db.String(255), default='0, 0, 0, 0, 0, 0')
    card_place3 = db.Column(db.String(255), default='0, 0, 0, 0, 0, 0')
    card_place = db.Column(db.String(255), default='0, 0, 0, 0, 0, 0')
    cards_now = db.Column(db.String(255), default='0, 0, 0, 0, 0, 0')
    speaker = db.Column(db.Integer, default=0)
    speaker_id = db.Column(db.Integer, default=0)
    stage = db.Column(db.Integer, default=0)
    lastdeal = db.Column(db.Integer)
    players_bet = db.Column(db.String(255), default='0, 0, 0, 0, 0, 0')
    hodor = db.Column(db.Integer, default=0)
    usersays = db.Column(db.String(255), default=',,,,,')
    top_bet = db.Column(db.Boolean, default=False)
    check = db.Column(db.String(255), default='False, False, False, False, False, False')
    status = db.Column(db.String(255), default='0, 0, 0, 0, 0, 0')
    turn1win = db.Column(db.Integer, default=0)
    turn2win = db.Column(db.Integer, default=0)
    turn3win = db.Column(db.Integer, default=0)
    current_hodor = db.Column(db.Integer, default=0)
    azi_price = db.Column(db.Integer, default=0)
    def __repr__(self):
        return '<Games %r>' % self.id

