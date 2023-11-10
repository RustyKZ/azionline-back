from app.support_functions import *
from flask import jsonify, request, redirect
from app.classes import *
import time
from app.sockets import *
import random
import math

def get_404_page(user_id):
    player = None
    try:
        player = Players.query.get(user_id)
    except:
        return jsonify({'message': f'User {user_id} not found'}), 401
    if player is not None:
        return jsonify({'message': f'User {player.nickname} visited 404 page'},
                       {'user_id': player.id,
                        'table_id': player.active_table,
                        'user_nickname': player.nickname}), 200
    else:
        return jsonify({'message': f'User {user_id} not found'}), 401
def get_tables(user_id):
    p_a_t = 0
    if user_id != 0:
        player = Players.query.get(user_id)
        p_a_t = player.active_table
    tables = Tables.query.order_by(Tables.id).all()
    tables_data = []
    for table in tables:
        table_data = {
            'id': table.id,
            'max_players': table.max_players,
            'drop_suit': table.drop_suit,
            'cointype': table.cointype,
            'min_bet': table.min_bet,
            'max_bet': table.max_bet,
            'table_password': table.table_password,
            'players': table.players,
            'blind_game': table.blind_game,
            'dealing': table.dealing,
            'currentgame': table.currentgame,
            'players_now': table.players_now,
            'sort_index': table.sort_index,
            'time_stop': table.time_stop,
        }
        tables_data.append(table_data)

    player_names = {}
    player_reputation = {}
    player_rating = {}
    players = Players.query.all()

    for player in players:
        player_names[player.id] = player.nickname
        player_reputation[player.id] = player.reputation
        player_rating[player.id] = player.rating
    players_matrix = []
    for tab in tables:
        players_matrix.append(get_array(tab.players))

    data = {
        'tables_data': tables_data,
        'player_names': player_names,
        'player_reputation': player_reputation,
        'player_rating': player_rating,
        'player_matrix': players_matrix,
        'player_active_table': p_a_t
    }
    return jsonify(data)

def game_join_table(data):
    user_id = data.get('user_id')
    table_id = data.get('table_id')
    table_password = data.get('table_password')

    player = Players.query.get(user_id)
    table = Tables.query.get(table_id)
    current_table_password = table.table_password

    # Предварительная проверка корректновти пользователя, стола и пароля
    if not player:
        print(f'GAME JOIN TABLE: User {user_id} not found')
        return jsonify({'message': f'User {user_id} not found'}), 401
    if not table:
        print(f'GAME JOIN TABLE: Table {table_id} not found')
        return jsonify({'message': f'Table {table_id} not found'}), 204
    if current_table_password and table_password != current_table_password:
        print(f'GAME JOIN TABLE: Table #{table_id} password incorrect')
        print('GAME JOIN TABLE: Front: ', table_password, '; Back: ', current_table_password,';')
        return jsonify({'message': f'Table #{table_id} password incorrect'}), 403

    # Проверка наличния данного игрока за столом и свободных мест
    already_here = False
    table_players = get_array(table.players)
    print('GAME JOIN TABLE: Table Players', table_players)
    no_seats = True
    if table.players_now != 0:
        for pp in range(1, table.max_players + 1):
            if table_players[pp - 1] == user_id:
                already_here = True
            if table_players[pp - 1] != 0:
                print('GAME JOIN TABLE: Seat', pp, ' of ', table.max_players, ' - User', table_players[pp - 1])
            else:
                no_seats = False
    else:
        no_seats = False

    # Проверка баланса пользователя
    no_coin = True
    if table.cointype == 0:
        if player.freecoin >= table.min_bet:
            no_coin = False
    elif table.cointype == 1:
        if player.goldcoin >= table.min_bet:
            no_coin = False
    else:
        pass

    if player.active_table != 0 and not already_here:
        print(f'GAME JOIN TABLE: {player.nickname} is already at table {player.active_table}, tries to sit at table {table.id}')
        return jsonify({'message': f'{player.nickname} is already at table {player.active_table}, tries to sit at {table.id}'}), 401
    if no_seats and not already_here:
        print(f'GAME JOIN TABLE: {player.nickname} tries to sit at table {table.id}, but no empty seats there')
        return jsonify({'message': f'{player.nickname} tries to sit at table {table.id}, but no empty seats there'}), 401
    if no_coin:
        print(f'GAME JOIN TABLE: {player.nickname} tries to sit at table {table.id} but he is too poor for playing there')
        return jsonify({'message': f'User {player.nickname} tries to sit at table {table.id} but too poor'}), 401
    # Проверки пройдены, присоединение или возвращение пользователя к столу

    if player.active_table == table.id and already_here:
        print(f'GAME JOIN TABLE: {player.nickname} returns to table {table.id}')
    else:
        table_players = get_array(table.players)
        # Собственно, прсоединение пользователя к столу с обновлением БД
        for pp in range(1, table.max_players + 1):
            if table_players[pp - 1] == 0:
                table_players[pp - 1] = player.id
                print('GAME JOIN TABLE: User tryes to use ', pp, ' seat ')
                player.active_table = table.id
                table.players_now += 1
                table.players = set_array(table_players)
                table.time_stop = 0
                db.session.commit()
                print(f'GAME JOIN TABLE: {player.nickname} has joined on the table {table.id}')
                break
        try:
            game = Games.query.get(table.currentgame)
            if game.stage == 0 or game.stage == 11:
                game.lastdeal = int(time.time())
                db.session.commit()
        except:
            pass
            # Создание словаря никнеймов
    player_names = {}
    players = Players.query.order_by(Players.id).all()
    for p in players:
        player_names[p.id] = p.nickname
    table = Tables.query.filter_by(id=table_id).first()
    table_players = get_array(table.players)
    this_table = {
        'id': table.id,
        'max_players': table.max_players,
        'drop_suit': table.drop_suit,
        'cointype': table.cointype,
        'min_bet': table.min_bet,
        'max_bet': table.max_bet,
        'table_password': table.table_password,
        'players': table_players,
        'blind_game': table.blind_game,
        'dealind': table.dealing,
        'currentgame': table.currentgame,
        'players_now': table.players_now,
        'sort_index': table.sort_index,
        'time_stop': table.time_stop,
        'interval' : table.interval
    }
    return jsonify({'message': f'User {player.nickname} joined to the table {table.id}'},
                       {'player_names': player_names,
                        'table': this_table}), 200


def game_get_table(data):
    user_id = data.get('user_id')
    table_id = data.get('table_id')
    player = None
    table = None
    try:
        player = Players.query.get(user_id)
        table = Tables.query.get(table_id)
        # print(f'GAME_GET_TABLE: User ID - {user_id}, table_ID - {table_id}')
    except:
        print(f'GAME_GET_TABLE: incorrect data')
        return jsonify({'message': f'User {user_id} not found'}), 206
    if not player or player is None:
        print(f'User not {user_id} found')
        return jsonify({'message': f'User {user_id} not found'}), 204
    if not table or table is None:
        print(f'Table {table_id} not found')
        return jsonify({'message': f'Table {table_id} not found'}), 204
    if table.cointype == 0:
        balance = player.freecoin
    else:
        balance = player.goldcoin

    game = Games.query.get(table.currentgame)
    game_status = get_array(game.status)
    arr_players = get_array(game.players)
    player_names = {}
    player_statuses = {}
    for st in range(0,6):
        if arr_players[st] != 0:
            player_statuses[arr_players[st]] = game_status[st]

    players = Players.query.order_by(Players.id).all()
    for p in players:
        player_names[p.id] = p.nickname

    table = Tables.query.filter_by(id=table_id).first()
    table_players = get_array(table.players)
    this_table = {
        'id': table.id,
        'max_players': table.max_players,
        'drop_suit': table.drop_suit,
        'cointype': table.cointype,
        'min_bet': table.min_bet,
        'max_bet': table.max_bet,
        'table_password': table.table_password,
        'players': table_players,
        'blind_game': table.blind_game,
        'dealing': table.dealing,
        'currentgame': table.currentgame,
        'players_now': table.players_now,
        'sort_index': table.sort_index,
        'time_stop': table.time_stop,
        'interval': table.interval
    }

    arr_card_deck = get_array(game.card_deck)
    arr_card_players = get_array(game.card_players)
    arr_card_place1 = get_array(game.card_place1)
    arr_card_place2 = get_array(game.card_place2)
    arr_card_place3 = get_array(game.card_place3)
    arr_card_place = get_array(game.card_place)
    arr_cards_now = get_array(game.cards_now)
    arr_players_bet = get_array(game.players_bet)
    arr_game_status = get_array(game.status)
    arr_usersays = get_string_array(game.usersays)
    arr_game_check = get_bool_array(game.check)
    this_game = {
        'id': game.id,
        'start_game': game.start_game,
        'table_id': game.table_id,
        'players': arr_players,
        'min_bet': game.min_bet,
        'drop_suit': game.drop_suit,
        'trump_suit': game.trump_suit,
        'pot': game.pot,
        'betting': game.betting,
        'gaming': game.gaming,
        'end_game': game.end_game,
        'winner': game.winner,
        'lastgame': game.lastgame,
        'card_deck': arr_card_deck,
        'card_players': arr_card_players,
        'card_place1': arr_card_place1,
        'card_place2': arr_card_place2,
        'card_place3': arr_card_place3,
        'card_place': arr_card_place,
        'cards_now': arr_cards_now,
        'speaker': game.speaker,
        'speaker_id': game.speaker_id,
        'stage': game.stage,
        'lastdeal': game.lastdeal,
        'players_bet': arr_players_bet,
        'hodor': game.hodor,
        'usersays': arr_usersays,
        'top_bet': game.top_bet,
        'check': arr_game_check,
        'status': arr_game_status,
        'turn1win': game.turn1win,
        'turn2win': game.turn2win,
        'turn3win': game.turn3win,
        'current_hodor': game.current_hodor,
        'azi_price' :game.azi_price
    }
    return jsonify({'message': f'Update information about table {table.id}'},
                   {'player_names': player_names,
                    'player_statuses': player_statuses,
                    'table': this_table,
                    'game': this_game,
                    'balance': balance}), 200


def game_leave_table(data):
    user_id = data.get('user_id')
    table_id = data.get('table_id')
    player = Players.query.get(user_id)
    table = Tables.query.get(table_id)
    if not player:
        print('User ' + player.nickname + ' not found')
        return jsonify({'message': f'User {player.nickname} not found'}), 401
    if not table:
        print(f'Table {table.id} not found')
        return jsonify({'message': f'Table {table.id} not found'}), 401
    else:
        drop_player(user_id, table_id)
        print(f'GAME_VEAVE_TABLE: User {player.nickname} left {table_id}')
        return jsonify({'message': f'User {player.nickname} left {table_id}'}), 200


def drop_player(player_id, table_id):
    player = Players.query.get(player_id)
    table = Tables.query.get(table_id)
    table_players = get_array(table.players)
    print(table_players)
    player_table_index = table_players.index(player_id)
    drop_this_player = True
    try:
        game = Games.query.get(table.currentgame)
        game_players = get_array(game.players)
        player_game_index = game_players.index(player_id)
        game_status = get_array(game.status)
        player_is_alone = True
        for i in range(0, 6):
            if game_players[i] != 0 and game_players[i] != player_id and game_status[i] != 1:
                player_is_alone = False
        if (game_status[player_game_index] == 0) or \
                (game_status[player_game_index] == 1) or \
                (game_status[player_game_index] == 9) or \
                (game_status[player_game_index] == 10) or \
                (game_status[player_game_index] == 12) or \
                (game_status[player_game_index] == 14) or \
                player_is_alone:
            pass
        else:
            drop_this_player = False
    except:
        try:
            game = Games.query.get(table.currentgame)
            game_players = get_array(game.players)
            if player_id in table_players and player_id not in game_players:
                pass
        except:
            drop_this_player = False

    if drop_this_player:
        player.active_table = 0
        # table cleaning
        table_players[player_table_index] = 0
        table.players_now -= 1
        if table.players_now == 0:
            time_stop = int(time.time())
            table.time_stop = time_stop
        table.players = set_array(table_players)
        # Переназначение дилера
        if table.dealing == player_table_index + 1:
            td = 0
            for nd in range(table.dealing, table.dealing + table.max_players):
                n = nd
                if nd >= table.max_players:
                    n = nd % table.max_players
                if table_players[n] != 0:
                    td = n + 1
                    break
            table.dealing = td
            print(f'DROP PLAYER : New dealer is {table.dealing}')
        db.session.commit()
        # game cleaning
        try:
            game = Games.query.get(table.currentgame)
            game_players = get_array(game.players)
            player_game_index = game_players.index(player_id)
            game_players[player_game_index] = 0
            game.players = set_array(game_players)
            card_players = get_array(game.card_players)
            for i in range(1, 5):
                card_players[(player_game_index * 4) + i] = 0
            game.card_players = set_array(card_players)
            players_bet = get_array(game.players_bet)
            players_bet[player_game_index] = 0
            game.players_bet = set_array(players_bet)
            new_usersays = get_string_array(game.usersays)  # Создаем копию массива
            new_usersays[player_game_index] = ''
            game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
            game_check = get_bool_array(game.check)
            game_check[player_game_index] = False
            game.check = set_bool_array(game_check)
            game_status = get_array(game.status)
            game_status[player_game_index] = 0
            game.status = set_array(game_status)
            db.session.commit()
            # Переназначение спикера
            if table.players_now <= 1:
                game.speaker = 0
                game.speaker_id = 0
            elif game.speaker == player_game_index + 1:
                game_players = get_array(game.players)
                gs = 0
                for ns in range(game.speaker, game.speaker + table.max_players):
                    n = gs
                    if gs >= table.max_players:
                        n = ns % table.max_players
                    if game_players[n] != 0:
                        game.speaker = n + 1
                        game.speaker_id = game_players[n]
                        break
                print(f'DROP PLAYER : New speaker is {game.speaker} user {game.speaker_id}')
            db.session.commit()
        except:
            print(f'DROP PLAYER : User {player.nickname} is not in the game !!!')
            pass
        print(f'DROP PLAYER : User {player.nickname} left table {table_id} !!!')
    else:
        print(f'DROP PLAYER : User {player.nickname} can not leave {table_id} now !!!')

def create_new_game(table_id):
    table = Tables.query.filter_by(id=table_id).first()
    table_players = get_array(table.players)
    players_quantity = 0
    for i in range(0,6):
        if table_players[i] != 0:
            player = Players.query.get(table_players[i])
            if ((table.cointype == 0) and (player.freecoin < table.min_bet)) or ((table.cointype == 1) and (player.goldcoin < table.min_bet)):
                drop_player(player.id, table_id)
                socketio.emit('update_tables', to='tables')
            else:
                players_quantity += 1
    if players_quantity < 1:
        return 0
    game_id = table.currentgame
    current_time = int(time.time())
    if (game_id is None) or (game_id == 0):
        new_game = Games(table_id=table.id, min_bet=table.min_bet, drop_suit=table.drop_suit, lastgame=0, lastdeal=current_time)
    else:
        new_game = Games(table_id=table.id, min_bet=table.min_bet, drop_suit=table.drop_suit, lastgame=game_id, lastdeal=current_time)
    db.session.add(new_game)
    db.session.commit()
    table.currentgame = new_game.id
    db.session.commit()
    return new_game.id

def start_new_game(game_id):
    game = Games.query.get(game_id)
    table_id = game.table_id
    table = Tables.query.get(table_id)
    table_players = get_array(table.players)
    game_players = table_players[:]
    game.players = set_array(game_players)
    db.session.commit()
    # Dealer determinating
    if game_players[table.dealing - 1] != 0:
        print(f'START_NEW_GAME: OLD dealer is pos {table.dealing} user {game_players[table.dealing - 1]}')
        pass
    else:
        for i in range(table.dealing, (table.dealing + 6)):
            nd_pos = i
            if i >= table.max_players:
                nd_pos = i % table.max_players
            if game_players[nd_pos] != 0:
                table.dealing = nd_pos + 1
                print(f'START_NEW_GAME: NEW dealer is pos {table.dealing} user {game_players[table.dealing - 1]}')
                db.session.commit()
                break
    # Speaker determinating
    speaker = 0
    speaker_id = 0
    for n in range(table.dealing + 1, table.dealing + table.max_players):
        ns = n
        if ns > table.max_players:
            ns = n % table.max_players
        if game_players[ns - 1] != 0:
            speaker = ns
            speaker_id = game_players[ns - 1]
            break
    game.speaker = speaker
    game.speaker_id = speaker_id
    print(f'START_NEW_GAME: NEW Speaker is {speaker_id}')
    db.session.commit()
    print(f'NEW Game # {game.id} started on Table {table_id}')


# Переназначение спикера
def nextspeaker(game_id):
    game = Games.query.filter_by(id=game_id).first()
    table = Tables.query.filter_by(id=game.table_id).first()
    table_players = get_array(table.players)
    gs = game.speaker
    for i in range(gs + 1, gs + table.max_players + 1):
        ps = i
        if i > table.max_players:
            ps = i % table.max_players
        if table_players[ps - 1] != 0:
            game.speaker = ps
            game.speaker_id = table_players[ps - 1]
            game.lastdeal = int(time.time())
            db.session.commit()
            break

def nextgamespeaker(game_id):
    game = Games.query.filter_by(id=game_id).first()
    table = Tables.query.filter_by(id=game.table_id).first()
    game_players = get_array(game.players)
    game_status = get_array(game.status)
    gs = game.speaker
    for i in range(gs + 1, gs + table.max_players + 1):
        ps = i
        if i > table.max_players:
            ps = i % table.max_players
        if (game_players[ps - 1] != 0) and (game_status[ps - 1] != 1) and (game_status[ps - 1] != 10) and (game_status[ps - 1] != 14):
            game.speaker = ps
            game.speaker_id = game_players[ps - 1]
            game.lastdeal = int(time.time())
            db.session.commit()
            break

def deal_cards(game_id):
    game = Games.query.get(game_id)
    table = Tables.query.get(game.table_id)
    table_players = get_array(table.players)
    # card_deck = get_array(game.card_deck)
    # card_players = get_array(game.card_players)
    card_deck = get_array('1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1')
    card_players = get_array('0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0')
    game_players = get_array(game.players)
    if game.drop_suit != 0:
        for i in range(0, 9):
            card_deck[game.drop_suit*9-9+i] = 0
    game.card_deck = set_array(card_deck)
    db.session.commit()
    game_status = get_array(game.status)
    card_deck = get_array(game.card_deck)
    actual_deck = []
    for i in range(0,36):
        if card_deck[i] != 0:
            actual_deck.append(i+1)
    print(actual_deck)
    trump_card = random.randint(0, len(actual_deck)-1)
    card_players[0] = actual_deck[trump_card]
    card_deck[actual_deck[trump_card]-1] = 0
    del actual_deck[trump_card]
    for cn in range(0, 4):
        for i in range(0, 6):
            if table_players[i] != 0 and table_players[i] in game_players and game_status[i] != 1 and game_status[i] != 10 and game_status[i] != 14:
                random_card = random.randint(0, len(actual_deck)-1)
                card_players[i*4 + cn + 1] = actual_deck[random_card]
                card_deck[actual_deck[random_card]-1] = 0
                del actual_deck[random_card]
    # Сортировка карт
    sort_criteria = [1, 10, 19, 28, 2, 11, 20, 29, 3, 12, 21, 30, 4, 13, 22, 31, 5, 14, 23, 32, 6, 15, 24, 33, 7, 16, 25, 34, 8, 17, 26, 35, 9, 18, 27, 36]
    sort_dict = {num: i for i, num in enumerate(sort_criteria)}
    trump = card_players[0]
    trump_offcet = 100
    for i in range(0, 6):
        temp_array = []
        for c in range(1, 5):
            card = card_players[i*4+c]
            if (1 <= trump <= 9) and (1 <= card <= 9):
                card += trump_offcet
            elif (10 <= trump <= 18) and (10 <= card <= 18):
                card += trump_offcet
            elif (19 <= trump <= 27) and (19 <= card <= 27):
                card += trump_offcet
            elif (28 <= trump <= 36) and (28 <= card <= 36):
                card += trump_offcet
            else:
                pass
            temp_array.append(card)
        temp_array.sort()
        temp_temp_array = [num for num in temp_array if num in sort_dict]
        sorted_temp_array = sorted(temp_temp_array, key=sort_dict.get)
        missing_nums = set(temp_array) - set(sort_dict.keys())
        sorted_array = sorted_temp_array + sorted(missing_nums)
        # print('Player pos.#', i + 1 , sorted_array)
        if sorted_array == [0]:
            sorted_array = [0, 0, 0, 0]
        for c in range(0, 4):
            card_players[i*4+c+1] = sorted_array[c] % trump_offcet
    game.card_deck = set_array(card_deck)
    game.card_players = set_array(card_players)
    game.stage = 3
    game.check = set_bool_array([False, False, False, False, False, False])
    db.session.commit()
    print(f'DEAL CARD: dealing is over, game.stage is {game.stage}')
    time.sleep(1)
    # current_gamestage(game_id)

def player_bet(player_id, game_id, value):
    game = Games.query.get(game_id)
    player = Players.query.get(player_id)
    table = Tables.query.get(game.table_id)
    game_players = get_array(game.players)
    playersbet = get_array(game.players_bet)
    if game.top_bet:
        return False
    for b in playersbet:
        if b != 0:
            return False
    player_pos = 0
    for i in range (0, 6):
        print('i = ', i, ' gameplayer = ', game_players[i], ' player_ID = ', player_id)
        if game_players[i] == player_id:
            player_pos = i
            print('PLAYERS POS IS ', player_pos)
            break

    if table.cointype == 0:
        if player.freecoin < value:
            return False
        else:
            player.freecoin = player.freecoin - value
            game.pot = game.pot + value
            playersbet[player_pos] = playersbet[player_pos] + value
            game.players_bet = set_array(playersbet)
            new_usersays = get_string_array(game.usersays)  # Создаем копию массива
            new_usersays[player_pos] = 'Bet ' + text_number(value)
            if value == game.min_bet * 10:
                game.top_bet = True
                new_usersays[player_pos] = 'TOP BET! ' + text_number(value)
            game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
            game.hodor = player_pos + 1
            game.current_hodor = player_pos + 1
            db.session.commit()
            return True
    elif table.cointype == 1:
        if player.goldcoin < value:
            return False
        else:
            player.goldcoin = player.goldcoin - value
            game.pot = game.pot + value
            playersbet[player_pos] = playersbet[player_pos] + value
            game.players_bet = set_array(playersbet)
            new_usersays = get_string_array(game.usersays)  # Создаем копию массива
            new_usersays[player_pos] = 'Bet ' + text_number(value)
            if value == game.min_bet * 10:
                game.top_bet = True
                new_usersays[player_pos] = 'TOP BET! ' + text_number(value)
            game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
            game.hodor = player_pos + 1
            game.current_hodor = player_pos + 1
            db.session.commit()
            return True

def player_check(player_id, game_id):
    game = Games.query.get(game_id)
    game_players = get_array(game.players)
    playersbet = get_array(game.players_bet)
    game_check = get_bool_array(game.check)
    game_status = get_array(game.status)
    for b in playersbet:
        if b != 0:
            return False
    player_pos = 0
    for i in range(0, 6):
        if game_players[i] == player_id:
            player_pos = i
            break
    player = Players.query.get(player_id)
    table = Tables.query.get(game.table_id)
    if table.cointype == 0:
        if player.freecoin < table.min_bet:
            game_status[player_pos] = 1
            game.status = set_array(game_status)
            new_usersays = get_string_array(game.usersays)  # Создаем копию массива
            new_usersays[player_pos] = 'Out of funds'
            game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
            db.session.commit()
            return True
    elif table.cointype == 1:
        if player.goldcoin < table.min_bet:
            game_status[player_pos] = 1
            game.status = set_array(game_status)
            new_usersays = get_string_array(game.usersays)  # Создаем копию массива
            new_usersays[player_pos] = 'Out of funds'
            game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
            db.session.commit()
            return True
    if game_check[player_pos] != True or 1 == 1:
        game_check[player_pos] = True
        new_usersays = get_string_array(game.usersays)  # Создаем копию массива
        new_usersays[player_pos] = 'Check'
        game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
        game.check = set_bool_array(game_check)
        print(f'PLAYER CHECK{game_check}')
        db.session.commit()
        return True
    else:
        return False

def check_checking(game_id):
    game = Games.query.get(game_id)
    game_players = get_array(game.players)
    table = Tables.query.get(game.table_id)
    players_check = get_bool_array(game.check)
    game_status = get_array(game.status)
    all_bets_are_check = True
    for i in range(0, 6):
        if (game_players[i] != 0) and (game_status[i] != 1) and (game_status[i] != 10) and (game_status[i] != 14):
            if players_check[i] != True:
                all_bets_are_check = False
                break
    check_poor_defeat(game_id)
    print('ALL BETS ARE CHECK: ', all_bets_are_check)
    if all_bets_are_check and (game.stage == 3):
        print('NEW DEALER STARTED')
        game.stage = 10
        db.session.commit()
        print('GAME STAGE ', game.stage)
        # New Dealer
        for i in range(table.dealing, (table.dealing + 6)):
            nd_pos = i
            # print('ND_POS = ', nd_pos)
            if i >= 6:
                nd_pos = i % 6
            # print('ND_POS UPDATED= ', nd_pos)
            if game_players[nd_pos] != 0:
                if game_status[nd_pos] == 2:
                    table.dealing = nd_pos + 1
                    db.session.commit()
                    print('NEW DEALER ', table.dealing)
                    break
        # New Speaker
        table = Tables.query.get(game.table_id)
        for i in range(table.dealing, table.dealing + 6):
            ns_pos = i
            if i >= 6:
                ns_pos = i % 6
            if game_players[ns_pos] != 0:
                if game_status[ns_pos] == 2:
                    game.speaker = ns_pos + 1
                    game.speaker_id = game_players[ns_pos]
                    db.session.commit()
                    print('NEW SPEAKER ', game.speaker)
                    break
        card_deck = get_array(
            '1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1')
        card_players = get_array('0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0')
        game.card_deck = set_array(card_deck)
        game.card_players = set_array(card_players)
        db.session.commit()
        print('DEALER UPDATED')
        time.sleep(1)
        current_gamestage(game_id)
        # start_rebet_all(game_id)

def player_call(player_id, game_id):
    game = Games.query.get(game_id)
    player = Players.query.get(player_id)
    table = Tables.query.get(game.table_id)
    game_players = get_array(game.players)
    playersbet = get_array(game.players_bet)
    player_pos = 0
    for i in range (0, 6):
        if game_players[i] == player_id:
            player_pos = i
            break
    max_value = max(playersbet)
    value = max_value - playersbet[player_pos]
    if value < 0:
        return False
    if table.cointype == 0:
        if player.freecoin < value:
            return False
        else:
            player.freecoin = player.freecoin - value
            game.pot = game.pot + value
            playersbet[player_pos] = playersbet[player_pos] + value
            game.players_bet = set_array(playersbet)
            new_usersays = get_string_array(game.usersays)  # Создаем копию массива
            new_usersays[player_pos] = 'Call ' + text_number(value)
            game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
            db.session.commit()
            return True
    elif table.cointype == 1:
        if player.goldcoin < value:
            return False
        else:
            player.goldcoin = player.goldcoin - value
            game.pot = game.pot + value
            playersbet[player_pos] = playersbet[player_pos] + value
            game.players_bet = set_array(playersbet)
            new_usersays = get_string_array(game.usersays)  # Создаем копию массива
            new_usersays[player_pos] = 'Call ' + text_number(value)
            game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
            db.session.commit()
            return True
def call_checking(game_id):
    game = Games.query.get(game_id)
    game_players = get_array(game.players)
    players_bet = get_array(game.players_bet)
    game_status = get_array(game.status)
    all_bets_are_off = True
    max_value = max(players_bet)
    if max_value == 0:
        all_bets_are_off = False
    for i in range(0, 6):
        if game_players[i] != 0 and game_status[i] != 1 and game_status[i] != 10 and game_status[i] != 14:
            print(i, max_value)
            if players_bet[i] != max_value:
                all_bets_are_off = False
                break
    if all_bets_are_off:
        game.stage = 4
        game.speaker = game.hodor
        for i in range(1, 7):
            if i == game.speaker:
                game.speaker_id = game_players[i-1]
        db.session.commit()

def player_raise(player_id, game_id, raise_value):
    game = Games.query.get(game_id)
    player = Players.query.get(player_id)
    table = Tables.query.get(game.table_id)
    game_players = get_array(game.players)
    playersbet = get_array(game.players_bet)
    player_pos = 0
    for i in range (0, 6):
        if game_players[i] == player_id:
            player_pos = i
            break
    max_value = max(playersbet)
    call_value = max_value - playersbet[player_pos]
    if call_value < 0:
        return False
    if game.top_bet:
        return False
    full_value = call_value + raise_value

    if table.cointype == 0:
        if player.freecoin < full_value:
            return False
        else:
            player.freecoin = player.freecoin - full_value
            game.pot = game.pot + full_value
            playersbet[player_pos] = playersbet[player_pos] + full_value
            game.players_bet = set_array(playersbet)
            new_usersays = get_string_array(game.usersays)  # Создаем копию массива
            new_usersays[player_pos] = 'Call ' + text_number(call_value) + ' | Raise ' + text_number(raise_value)
            if raise_value == game.min_bet * 10:
                game.top_bet = True
                new_usersays[player_pos] = 'Call ' + text_number(call_value) + ' | TOP RAISE! ' + text_number(raise_value)
            game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
            game.hodor = player_pos + 1
            game.current_hodor = player_pos + 1
            db.session.commit()
            return True
    elif table.cointype == 1:
        if player.goldcoin < full_value:
            return False
        else:
            player.goldcoin = player.goldcoin - full_value
            game.pot = game.pot + full_value
            playersbet[player_pos] = playersbet[player_pos] + full_value
            game.players_bet = set_array(playersbet)
            new_usersays = get_string_array(game.usersays)  # Создаем копию массива
            new_usersays[player_pos] = 'Call ' + text_number(call_value) + ' | Raise ' + text_number(raise_value)
            if raise_value == game.min_bet * 10:
                game.top_bet = True
                new_usersays[player_pos] = 'Call ' + text_number(call_value) + ' | TOP RAISE! ' + text_number(raise_value)
            game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
            game.hodor = player_pos + 1
            game.current_hodor = player_pos + 1
            db.session.commit()
            return True
def player_fold(player_id, game_id):
    game = Games.query.get(game_id)
    game_players = get_array(game.players)
    game_status = get_array(game.status)
    for pl in range (0, 6):
        if game_players[pl] == player_id:
            game_status[pl] = 10
            game.status = set_array(game_status)
            new_usersays = get_string_array(game.usersays)  # Создаем копию массива
            new_usersays[pl] = 'Fold'
            game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
            # Сбрасываем карты
            card_players = get_array(game.card_players)
            game_players = get_array(game.players)
            player_index = game_players.index(player_id)
            for cd in range(1, 5):
                card_players[(player_index * 4) + cd] = 0
            game.card_players = set_array(card_players)
            db.session.commit()
            return True
    return False

def fold_checking(game_id):
    game = Games.query.get(game_id)
    game_players = get_array(game.players)
    game_status = get_array(game.status)
    potential_winners = 0
    winner_pos = 0
    winner_id = 0
    for i in range(0, 6):
        if (game_status[i] != 0) and (game_status[i] != 1) and (game_status[i] != 10) and (game_status[i] != 14) and (game_players[i] !=0):
            potential_winners += 1
            winner_pos = i + 1
            winner_id = game_players[i]
    if potential_winners == 1:
        endgame_winner(game_id, winner_pos, winner_id)

def endgame_winner(game_id, winner_pos, winner_id):
    game = Games.query.get(game_id)
    table = Tables.query.get(game.table_id)
    game.winner = winner_pos
    table.dealing = game.winner
    player = Players.query.get(winner_id)
    if table.cointype == 0:
        player.freecoin += game.pot
    elif table.cointype == 1:
        player.goldcoin += game.pot
    game.end_game = datetime.utcnow()
    game.stage = 11
    game_status = get_array(game.status)
    game_status[winner_pos - 1] = 0
    game.status = set_array(game_status)
    db.session.commit()
    print(f'ENDGAME WINNER: {player.nickname} wins {game.pot} in game {game_id}')
    current_gamestage(game_id)

def player_drop_extra_card(game_id, user_id, card_id):
    game = Games.query.get(game_id)
    card_players = get_array(game.card_players)
    game_players = get_array(game.players)
    card_index = card_players.index(card_id)
    player_index = game_players.index(user_id)
    game_status = get_array(game.status)
    if game_status[player_index] == 6:
        print(f'PLAYER DROP EXTRA CARD: Error - Player {user_id} wants to drop second card')
        return False
    if (card_index >player_index * 4) and (card_index <= (player_index * 4) + 4):
        card_players[card_index] = 0
        game_status[player_index] = 6
        game.card_players = set_array(card_players)
        game.status = set_array(game_status)
        db.session.commit()
        print(f'PLAYER DROP CARD: succesfully - Player {user_id} dropped card {card_id}')
        return True
    return False

def player_drop_extra_card_checking(game_id):
    game = Games.query.get(game_id)
    game_players = get_array(game.players)
    game_status = get_array(game.status)
    all_extra_cards_dropeed = True
    for i in range(0, 6):
        if (game_status[i] != 0) and (game_status[i] != 1) and (game_status[i] != 10) and (game_players[i] !=0):
            if game_status[i] != 6:
                all_extra_cards_dropeed = False
    if all_extra_cards_dropeed:
        game.stage = 5
        game.speaker = game.hodor
        for i in range(1, 7):
            if i == game.speaker:
                game.speaker_id = game_players[i-1]
        game.lastdeal = int(time.time())
        db.session.commit()

def turn_checking(card_players, card_place, card_id, player_index, hodor):
    card_index = card_players.index(card_id)
    hodor_index = hodor - 1
    if (card_index > player_index * 4) and (card_index <= (player_index * 4) + 4) and (card_id != 0):
        if all(element == 0 for element in card_place) and (hodor_index == player_index):
            return True
        elif card_place[hodor_index] != 0:
            range_hodor = range( ((card_place[hodor_index] - 1) // 9) * 9 + 1, ((card_place[hodor_index] - 1) // 9) * 9 + 10)
            range_trump = range( ((card_players[0] - 1) // 9) * 9 + 1, ((card_players[0] - 1) // 9) * 9 + 10)
            if card_id in range_hodor:
                print('TURN CHECKING: good suit!')
                return True
            elif card_id in range_trump:
                no_hodor = True
                for ci in range(1, 5):
                    cc = card_players[player_index * 4 + ci]
                    if cc in range_hodor:
                        no_hodor = False
                if no_hodor:
                    print('TURN CHECKING: good Trump suit!')
                    return True
                else:
                    print('TURN CHECKING ERROR: You have to drop good SUIT!')
                    return False
            else:
                no_hodor = True
                for ci in range(1, 5):
                    cc = card_players[player_index * 4 + ci]
                    if cc in range_hodor:
                        no_hodor = False
                no_trump = True
                for ci in range(1, 5):
                    cc = card_players[player_index * 4 + ci]
                    if cc in range_trump:
                        no_trump = False
                if no_hodor and no_trump:
                    print('TURN CHECKING: good poor suit!')
                    return True
                else:
                    print('TURN CHECKING ERROR: You have to drop good suit or trump suit!')
                    return False
    print('TURN_CHECKING: error')
    return False


def player_turn_1(game_id, user_id, card_id):
    game = Games.query.get(game_id)
    card_players = get_array(game.card_players)
    card_place = get_array(game.card_place)
    game_players = get_array(game.players)
    card_index = card_players.index(card_id)
    player_index = game_players.index(user_id)
    if player_index != game.current_hodor - 1:
        print('PLAYER_TURN_1 ERROR: Not Hodor!!!')
        return False
    game_status = get_array(game.status)
    if game.stage != 5:
        print('PLAYER_TURN_1 ERROR: Bad time for turn #1!')
        return False
    if turn_checking(card_players, card_place, card_id, player_index, game.hodor):
        card_players[card_index] = 0
        card_place[player_index] = card_id
        game_status[player_index] = 7
        game.card_players = set_array(card_players)
        game.card_place = set_array(card_place)
        game.status = set_array(game_status)
        #New CurrentHodor
        gh = game.current_hodor
        for i in range(gh + 1, gh + 7):
            ps = i
            if i > 6:
                ps = i % 6
            if (game_players[ps - 1] != 0 and game_status[ps - 1] == 6) or (game_players[ps - 1] != 0 and game_status[ps - 1] == 7):
                game.current_hodor = ps
                game.speaker = ps
                game.speaker_id = game_players[ps - 1]
                game.lastdeal = int(time.time())
                db.session.commit()
                break
        db.session.commit()
        print(f'PLAYER TURN #1: succesfully - Player {user_id} turn card {card_id}')
        return True
    print(f'PLAYER TURN #1: ERROR - Player {user_id} try to turn card {card_id}')
    return False

def player_turn_2(game_id, user_id, card_id):
    game = Games.query.get(game_id)
    card_players = get_array(game.card_players)
    card_place = get_array(game.card_place)
    game_players = get_array(game.players)
    card_index = card_players.index(card_id)
    player_index = game_players.index(user_id)
    if player_index != game.current_hodor - 1:
        print('PLAYER_TURN_2 ERROR: Not Hodor!!!')
        return False
    game_status = get_array(game.status)
    if game.stage != 6:
        print('PLAYER_TURN_1 ERROR: Bad time for turn #2!')
        return False
    if turn_checking(card_players, card_place, card_id, player_index, game.hodor):
        card_players[card_index] = 0
        card_place[player_index] = card_id
        game_status[player_index] = 8
        game.card_players = set_array(card_players)
        game.card_place = set_array(card_place)
        game.status = set_array(game_status)
        #New CurrentHodor
        gh = game.current_hodor
        for i in range(gh + 1, gh + 7):
            ps = i
            if i > 6:
                ps = i % 6
            if (game_players[ps - 1] != 0 and game_status[ps - 1] == 7) or (game_players[ps - 1] != 0 and game_status[ps - 1] == 8):
                game.current_hodor = ps
                game.speaker = ps
                game.speaker_id = game_players[ps - 1]
                game.lastdeal = int(time.time())
                db.session.commit()
                break
        db.session.commit()
        print(f'PLAYER TURN #2: succesfully - Player {user_id} turn card {card_id}')
        return True
    print(f'PLAYER TURN #2: ERROR - Player {user_id} try to turn card {card_id}')
    return False

def player_turn_3(game_id, user_id, card_id):
    game = Games.query.get(game_id)
    card_players = get_array(game.card_players)
    card_place = get_array(game.card_place)
    game_players = get_array(game.players)
    card_index = card_players.index(card_id)
    player_index = game_players.index(user_id)
    if player_index != game.current_hodor - 1:
        print('PLAYER_TURN_3 ERROR: Not Hodor!!!')
        return False
    game_status = get_array(game.status)
    if game.stage != 7:
        print('PLAYER_TURN_3 ERROR: Bad time for turn #3!')
        return False
    if turn_checking(card_players, card_place, card_id, player_index, game.hodor):
        card_players[card_index] = 0
        card_place[player_index] = card_id
        game_status[player_index] = 9
        game.card_players = set_array(card_players)
        game.card_place = set_array(card_place)
        game.status = set_array(game_status)
        #New CurrentHodor
        gh = game.current_hodor
        for i in range(gh + 1, gh + 7):
            ps = i
            if i > 6:
                ps = i % 6
            if (game_players[ps - 1] != 0 and game_status[ps - 1] == 8) or (game_players[ps - 1] != 0 and game_status[ps - 1] == 9):
                game.current_hodor = ps
                game.speaker = ps
                game.speaker_id = game_players[ps - 1]
                game.lastdeal = int(time.time())
                db.session.commit()
                break
        db.session.commit()
        print(f'PLAYER TURN #3: succesfully - Player {user_id} turn card {card_id}')
        return True
    print(f'PLAYER TURN #3: ERROR - Player {user_id} try to turn card {card_id}')
    return False

def turn_winner(card_place, hodor_card, trump_card):
    range_hodor = range(((hodor_card - 1) // 9) * 9 + 1, ((hodor_card - 1) // 9) * 9 + 10)
    range_trump = range(((trump_card - 1) // 9) * 9 + 1, ((trump_card - 1) // 9) * 9 + 10)
    print(f'TURN WINNER: Range_hodor is {range_hodor}; Range_trump is {range_trump}; Card place is {card_place}')
    card_compare = [0] * 6
    for i in range(0, 6):
        if card_place[i] in range_hodor:
            card_compare[i] = card_place[i] + 100
        elif card_place[i] in range_trump:
            card_compare[i] = card_place[i] + 200
        else:
            card_compare[i] = card_place[i]
    print(f'TURN WINNER: card_compare is {card_compare}')
    best_hand = card_compare.index(max(card_compare))
    print(f'TURN_WINNER: Best hand is {best_hand}')
    return best_hand
def player_turn_1_checking(game_id):
    game = Games.query.get(game_id)
    card_players = get_array(game.card_players)
    card_place = get_array(game.card_place)
    card_place1 = get_array(game.card_place1)
    game_players = get_array(game.players)
    game_status = get_array(game.status)
    all_players_turned_1 = True
    for i in range(0, 6):
        if (game_status[i] != 0) and (game_status[i] != 1) and (game_status[i] != 10) and (game_players[i] != 0):
            if game_status[i] != 7:
                all_players_turned_1 = False
    print(f'PLAYER_TURN #1 CHECKING: all_players_turned_1 is {all_players_turned_1}')
    if all_players_turned_1:
        game.stage = 6
        hodor_card = card_place[game.hodor - 1]
        trump = card_players[0]
        print(f'PLAYER_TURN #1 CHECKING: TURN WINNER runned')
        game.turn1win = turn_winner(card_place, hodor_card, trump) + 1
        print(f'PLAYER_TURN #1 CHECKING: TURN WINNER complete, winner is {game.turn1win}')
        for i in range(0, 6):
            cp = i + game.hodor - 1
            if cp >= 6:
                cp = cp % 6
            card_place1[i] = card_place[cp]
        game.card_place1 = set_array(card_place1)
        game.card_place = '0, 0, 0, 0, 0, 0'
        game.hodor = turn_winner(card_place, hodor_card, trump) + 1
        game.current_hodor = game.hodor
        game.speaker = turn_winner(card_place, hodor_card, trump)
        for i in range(1, 7):
            if i == game.speaker:
                game.speaker_id = game_players[i - 1]
        db.session.commit()
        print('PLAYER_TURN #1 CHECKING: All players turned!')
def player_turn_2_checking(game_id):
    game = Games.query.get(game_id)
    card_players = get_array(game.card_players)
    card_place = get_array(game.card_place)
    card_place2 = get_array(game.card_place2)
    game_players = get_array(game.players)
    game_status = get_array(game.status)
    all_players_turned_2 = True
    for i in range(0, 6):
        if (game_status[i] != 0) and (game_status[i] != 1) and (game_status[i] != 10) and (game_players[i] != 0):
            if game_status[i] != 8:
                all_players_turned_2 = False
    print(f'PLAYER_TURN #2 CHECKING: all_players_turned_2 is {all_players_turned_2}')
    if all_players_turned_2:
        game.stage = 7
        hodor_card = card_place[game.hodor - 1]
        trump = card_players[0]
        print(f'PLAYER_TURN #2 CHECKING: TURN WINNER runned')
        game.turn2win = turn_winner(card_place, hodor_card, trump) + 1
        print(f'PLAYER_TURN #2 CHECKING: TURN WINNER complete, winner is {game.turn2win}')
        for i in range(0, 6):
            cp = i + game.hodor - 1
            if cp >= 6:
                cp = cp % 6
            card_place2[i] = card_place[cp]
        game.card_place2 = set_array(card_place2)
        game.card_place = '0, 0, 0, 0, 0, 0'
        game.hodor = turn_winner(card_place, hodor_card, trump) + 1
        game.current_hodor = game.hodor
        game.speaker = turn_winner(card_place, hodor_card, trump)
        for i in range(1, 7):
            if i == game.speaker:
                game.speaker_id = game_players[i - 1]
        db.session.commit()
        print('PLAYER_TURN #3 CHECKING: All players turned!')

def player_turn_3_checking(game_id):
    game = Games.query.get(game_id)
    card_players = get_array(game.card_players)
    card_place = get_array(game.card_place)
    card_place3 = get_array(game.card_place3)
    game_players = get_array(game.players)
    game_status = get_array(game.status)
    all_players_turned_3 = True
    for i in range(0, 6):
        if (game_status[i] != 0) and (game_status[i] != 1) and (game_status[i] != 10) and (game_players[i] != 0):
            if game_status[i] != 9:
                all_players_turned_3 = False
    print(f'PLAYER_TURN #2 CHECKING: all_players_turned_3 is {all_players_turned_3}')
    if all_players_turned_3:
        hodor_card = card_place[game.hodor - 1]
        trump = card_players[0]
        print(f'PLAYER_TURN #3 CHECKING: TURN WINNER runned')
        game.turn3win = turn_winner(card_place, hodor_card, trump) + 1
        print(f'PLAYER_TURN #3 CHECKING: TURN WINNER complete, winner is {game.turn3win}')
        for i in range(0, 6):
            cp = i + game.hodor - 1
            if cp >= 6:
                cp = cp % 6
            card_place3[i] = card_place[cp]
        game.card_place3 = set_array(card_place3)
        game.card_place = '0, 0, 0, 0, 0, 0'
        game.hodor = turn_winner(card_place, hodor_card, trump) + 1
        game.current_hodor = game.hodor
        game.speaker = turn_winner(card_place, hodor_card, trump)
        for i in range(1, 7):
            if i == game.speaker:
                game.speaker_id = game_players[i - 1]
        game.stage = 8
        db.session.commit()
        game = Games.query.get(game_id)
        print('PLAYER_TURN #3 CHECKING: All players turned!')
        if (game.turn1win == game.turn2win) or (game.turn1win == game.turn3win) or (game.turn2win == game.turn3win):
            end_game(game_id)
        else:
            azi_start(game_id)

def end_game(game_id):
    print('END_GAME: started')
    game = Games.query.get(game_id)
    game_players = get_array(game.players)
    game_status = get_array(game.status)
    winner_pos = None
    if (game.turn1win == game.turn2win):
        winner_pos = game.turn1win
    elif (game.turn1win == game.turn3win):
        winner_pos = game.turn1win
    elif (game.turn2win == game.turn3win):
        winner_pos = game.turn2win
    print(f'END_GAME: Winner_pos is {winner_pos}')
    winner_id = game_players[winner_pos - 1]
    game.winner = winner_pos
    player = Players.query.get(winner_id)
    table = Tables.query.get(game.table_id)
    table.dealing = winner_pos

    if table.cointype == 0:
        player.freecoin += game.pot
    elif table.cointype == 1:
        player.goldcoin += game.pot
    game.stage = 11
    game.end_game = datetime.utcnow()

    for i in range(0, 6):
        if game_status[i] == 1:
            drop_player(game_players[i], table.id)
            socketio.emit('update_tables', to='tables')
    db.session.commit()

    print(f'END_GAME: Game {game_id} is over, {player.nickname} wins {game.pot}')
    socketio.emit('update_room', to='table-' + str(table.id))
    current_gamestage(table.id)


def azi_start(game_id):
    game = Games.query.get(game_id)
    game_status = get_array(game.status)
    print(f'AZI START: Game {game_id} is draw, players in AZI')
    for i in range(0, 6):
        if (game_status[i] == 9) and ((game.turn1win - 1 == i) or (game.turn2win - 1 == i) or (game.turn3win - 1 == i)):
            game_status[i] = 11
            print(f'Players pos {i+1} in AZI')
        elif (game_status[i] == 9) or (game_status[i] == 10):
            game_status[i] = 12
            print(f'Players pos {i + 1} not in AZI')
    game.stage = 9
    game.status = set_array(game_status)
    game.azi_price = math.floor(game.pot / 2)
    game.usersays = set_string_array(['', '', '', '', '', ''])
    game.check = set_bool_array([False, False, False, False, False, False])
    game.hodor = 0
    db.session.commit()
    socketio.emit('update_room', to='table-' + str(game.table_id))
    current_gamestage(game_id)

def player_azi_in(game_id, player_id):
    game = Games.query.get(game_id)
    player = Players.query.get(player_id)
    table = Tables.query.get(game.table_id)
    game_players = get_array(game.players)
    player_pos = game_players.index(player_id)
    game_status = get_array(game.status)
    value = game.azi_price
    if game_status[player_pos] != 12:
        return False
    if table.cointype == 0:
        if player.freecoin < value:
            return False
        else:
            player.freecoin = player.freecoin - value
            game.pot = game.pot + value
            new_usersays = get_string_array(game.usersays)  # Создаем копию массива
            new_usersays[player_pos] = 'Burst into AZI for ' + text_number(value)
            game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
            game_status[player_pos] = 13
            game.status = set_array(game_status)
            db.session.commit()
            return True
    elif table.cointype == 1:
        if player.goldcoin < value:
            return False
        else:
            player.goldcoin = player.goldcoin - value
            game.pot = game.pot + value
            new_usersays = get_string_array(game.usersays)  # Создаем копию массива
            new_usersays[player_pos] = 'Burst into AZI for ' + text_number(value)
            game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
            game_status[player_pos] = 13
            game.status = set_array(game_status)
            db.session.commit()
            socketio.emit('update_room', to='table-' + str(table.id))
            return True

def player_azi_out(game_id, player_id):
    game = Games.query.get(game_id)
    game_players = get_array(game.players)
    player_pos = game_players.index(player_id)
    game_status = get_array(game.status)
    if game_status[player_pos] != 12:
        return False
    try:
        new_usersays = get_string_array(game.usersays)  # Создаем копию массива
        new_usersays[player_pos] = 'Refuse of AZI'
        game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
        game_status[player_pos] = 14
        game.status = set_array(game_status)
        db.session.commit()
        socketio.emit('update_room', to='table-' + str(game.table_id))
        print('PLAYER_AZI_OUT')
        return True
    except:
        return False

def player_azi_in_checking(game_id):
    game = Games.query.get(game_id)
    game_players = get_array(game.players)
    game_status = get_array(game.status)
    table = Tables.query.get(game.table_id)
    all_players_says = True
    for i in range(0, 6):
        if game_players[i] != 0 and game_status[i] != 1 and game_status[i] != 11 and game_status[i] != 13 and game_status[i] != 14:
            all_players_says = False
            break
    if all_players_says:
        game.stage = 1
        table.dealing = game.turn3win
        for p in range(0, 6):
            if game_status[p] == 11 or game_status[p] == 13:
                game_status[p] = 2
            if game_status[p] == 14:
                game_status[p] = 10
        game.status = set_array(game_status)
        gs = table.dealing = game.turn3win
        for i in range(gs + 1, gs + table.max_players + 1):
            ps = i
            if i > table.max_players:
                ps = i % table.max_players
            if (game_players[ps - 1] != 0) and (game_status[ps - 1] != 1) and (game_status[ps - 1] != 10):
                game.speaker = ps
                game.speaker_id = game_players[ps - 1]
                game.lastdeal = int(time.time())

                db.session.commit()
                break
        game.card_place1 = '0, 0, 0, 0, 0, 0'
        game.card_place2 = '0, 0, 0, 0, 0, 0'
        game.card_place3 = '0, 0, 0, 0, 0, 0'
        game.players_bet = '0, 0, 0, 0, 0, 0'
        game.top_bet = False
        db.session.commit()
        socketio.emit('update_room', to='table-' + str(table.id))
        print(f'PLAYER_AZI_CHECKING - successfully: New dealer is {table.dealing}, new Speaker is {game.speaker} (User {game.speaker_id})')
        current_gamestage(game_id)


def player_blind(player_id, game_id, value):
    game = Games.query.get(game_id)
    player = Players.query.get(player_id)
    table = Tables.query.get(game.table_id)
    game_players = get_array(game.players)
    playersbet = get_array(game.players_bet)
    if game.top_bet:
        return False
    for b in playersbet:
        if b != 0:
            return False
    player_pos = game_players.index(player_id)
    if table.cointype == 0:
        if player.freecoin < value:
            return False
        else:
            player.freecoin = player.freecoin - value
            game.pot = game.pot + value
            playersbet[player_pos] = playersbet[player_pos] + (value * 2)
            game.players_bet = set_array(playersbet)
            new_usersays = get_string_array(game.usersays)  # Создаем копию массива
            new_usersays[player_pos] = 'Blind Bet ' + text_number(value * 2)
            if value * 2 >= game.min_bet * 10:
                game.top_bet = True
                new_usersays[player_pos] = 'TOP BLIND BET! ' + text_number(value * 2)
            game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
            game.hodor = player_pos + 1
            game.current_hodor = player_pos + 1
            game.stage = 2
            db.session.commit()
            return True
    elif table.cointype == 1:
        if player.goldcoin < value:
            return False
        else:
            player.goldcoin = player.goldcoin - value
            game.pot = game.pot + value
            playersbet[player_pos] = playersbet[player_pos] + (value * 2)
            game.players_bet = set_array(playersbet)
            new_usersays = get_string_array(game.usersays)  # Создаем копию массива
            new_usersays[player_pos] = 'Blind Bet ' + text_number(value * 2)
            if value * 2 >= game.min_bet * 10:
                game.top_bet = True
                new_usersays[player_pos] = 'TOP BLIND BET! ' + text_number(value * 2)
            game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
            game.hodor = player_pos + 1
            game.current_hodor = player_pos + 1
            game.stage = 2
            db.session.commit()
            return True

# Легенда статуса игрока
    # Статус игрока (player.game_status)
    # 0 - ожидание
    # 1 - нет монет для игры
    # 2 - сделана стартовая ставка Ante
    # 3 - делает ставку - ?
    # 4 - поддерживает ставку - ?
    # 5 - повышает ставку - ?
    # 6 - окончены торги и сброшена карта
    # 7 - сделан 1-й ход
    # 8 - сделан 2-й ход
    # 9 - сделан 3-й ход
    # 10 - упал
    # 11 - в Ази
    # 12 - Вырезан из Ази
    # 13 - Вкупился в Ази
    # 14 - Отказался от Ази
    # 15 - Готов к следующей игре
    # 16 - Готов к текущей игре

# Легенда этапа игры (game.stage)
# 0 - игра не начата
# 1 - Ставки Анте сделаны
# 2 - Ставки втемную сделаны
# 3 - Карты розданы
# 4 - Ставки за первый ход сделаны, определены играющие и заходящий
# 5 - Лишняя карта сброшена
# 6 - Первый ход сделан
# 7 - Второй ход сделан
# 8 - Третий ход сделан, определен победитель или АЗИ
# 9 - Ожидание врезки в АЗИ
# 10- Все пасы, зарыли, добавление анте
# 11- Ожидание начала следующей игры


def new_game_full(table_id):
    # Создание новой игры
    game_id = create_new_game(table_id)
    if game_id != 0:
        start_new_game(game_id)
        current_gamestage(game_id)

def current_gamestage(game_id):
    game = Games.query.get(game_id)
    table_id = game.table_id
    table = Tables.query.get(table_id)
    # Стартовые ставки Анте
    if game.stage == 0:
        while game.stage == 0:
            start_bet_all(game_id)
            game = Games.query.get(game_id)
            if game.stage == 1:
                break
            socketio.emit('update_room', to='table-' + str(table_id))
        socketio.emit('update_room', to='table-' + str(table_id))
    if game.stage == 1:
        if table.blind_game == 0:
            game.stage = 2
            db.session.commit()
            socketio.emit('update_room', to='table-' + str(table_id))
    if game.stage == 2:
        deal_cards(game.id)
        socketio.emit('update_room', to='table-' + str(table_id))
    if game.stage == 3:
        pass
    if game.stage == 9:
        print('GAME STAGE 9: player_azi_in_checking(game_id)')
        time.sleep(2)
        player_azi_in_checking(game_id)
    if game.stage == 10:
        print('CURRENT GAMESTAGE 10: running StartRebetAll')
        start_rebet_all(game_id)
        socketio.emit('update_room', to='table-' + str(table_id))
    if game.stage == 11:
        check_money_for_game(game_id)
        game = Games.query.get(game_id)
        game_players = get_array(game.players)
        game_status = get_array(game.status)
        for i in range(0, 6):
            if game_status[i] == 1 and game_players[i] != 0:
                print(f'GAME STAGE 11: drop player {game_players[i]}')
                drop_player(game_players[i], game.table_id)
                socketio.emit('update_tables', to='tables')
    socketio.emit('update_room', to='table-' + str(table_id))

def check_money_for_game(game_id):
    game = Games.query.get(game_id)
    game_players = get_array(game.players)
    game_status = get_array(game.status)
    table = Tables.query.get(game.table_id)
    if table.cointype == 0:
        for i in range(0, 6):
            if game_players[i] != 0:
                player = Players.query.get(game_players[i])
                if player.freecoin < table.min_bet:
                    print(f'CHECK MONEY FOR GAME : user {game_players[i]} is too poor for playing in game {game_id}')
                    game_status[i] = 1
                    game.status = set_array(game_status)
                    db.session.commit()
    elif table.cointype == 1:
        for i in range(0, 6):
            if game_players[i] != 0:
                player = Players.query.get(game_players[i])
                if player.goldcoin < table.min_bet:
                    print(f'CHECK MONEY FOR GAME : user {game_players[i]} is too poor for playing in game {game_id}')
                    game_status[i] = 1
                    game.status = set_array(game_status)
                    db.session.commit()

def create_new_table(data):
    try:
        user_id = data.get('user_id')
        player = Players.query.get(user_id)
        if player.active_table != 0:
            print(f'CREATE NEW TABLE: Player cannot create new table, because his active table is {player.active_table}')
            return jsonify({'message': f'Player cannot create new table, because his active table is {player.active_table}'}), 401
        max_players = data.get('max_players')
        min_bet = data.get('min_bet')
        drop_suit = data.get('drop_suit')
        cointype = data.get('cointype')
        blind_game = data.get('blind_game')
        interval = data.get('interval')
        password = data.get('password')
        if (cointype == 0 and player.freecoin < min_bet) or (cointype == 1 and player.goldcoin < min_bet):
            print(f'CREATE NEW TABLE: Player cannot create new table, he is too poor')
            return jsonify({'message': f'Player cannot create new table, he is too poor'}), 401
        if max_players > 6 or max_players < 2 or min_bet < 1 or min_bet > 1000 or drop_suit < 0 or drop_suit > 4 or interval < 10 or interval > 60:
            print(f'CREATE NEW TABLE: Player cannot create new table, creating data incorrect')
            return jsonify({'message': f'Player cannot create new table, creating data incorrect'}), 401
        tables = Tables.query.all()
        tables_ids = [table.id for table in tables]
        new_id = find_min_missing_natural(tables_ids)
        print(f'CREATE NEW TABLE: {user_id} tryed to create a new table')
        new_table = Tables(
            id=new_id,
            max_players=max_players,
            drop_suit=drop_suit,
            cointype=cointype,
            min_bet=min_bet,
            max_bet=min_bet*10,
            table_password=password,
            interval=interval,
            blind_game=blind_game
        )
        print(f'CREATE NEW TABLE: {user_id} created a new table {new_table}')
        db.session.add(new_table)
        db.session.commit()
        table = Tables.query.get(new_id)
        table_players = get_array(table.players)
        table_players[0] = user_id
        table.players = set_array(table_players)
        table.players_now += 1
        player.active_table = new_id
        game = create_new_game(new_id)
        print(f'CREATE NEW TABLE: User {user_id} created a new table {new_table}. New game is #{game}')
        return jsonify({'message': f'New table created'}, {'table_id': new_id}), 200
    except:
        print('CREATE NEW TABLE: Incorrect data for table creating')
        return jsonify({'message': f'Incorrect data for table creating'}), 401

def game_default_action(table_id, game_id, user_id):
    socket_room = 'table-' + str(table_id)
    socket_data = {'user_id': 0, 'room-id': socket_room}
    table = Tables.query.get(table_id)
    game = Games.query.get(game_id)
    table_players = get_array(table.players)
    game_players = get_array(game.players)
    game_status = get_array(game.status)
    if user_id not in table_players:
        return jsonify({'message': f'Default action is running. User is not in this table'}), 206
    non_zero_players = [1 for element in table_players if element != 0]
    count_players = non_zero_players.count(1)
    if game.stage == 0 and count_players > 1:
        try:
            for i in range(0, 6):
                if table_players[i] != 0:
                    game_players[i] = table_players[i]
                    game_status[i] = 0
            game.status = set_array(game_status)
            game.players = set_array(game_players)
            game.lastdeal = int(time.time())
            db.session.commit()
            socketio.emit('update_room', socket_data, to=socket_room)
            start_new_game(game_id)
            current_gamestage(game_id)
            print(f'GAME DEFAULT ACTION: game {game_id} stage 00 - Good')
            return jsonify({'message': f'GAME DEFAULT ACTION: game stage 00 - Good'}), 200
        except:
            print(f'GAME DEFAULT ACTION: game {game_id} Except problem')
            pass
    if count_players == 1:
        game.lastdeal = int(time.time())
        db.session.commit()
        print('User is alone')
        return jsonify({'message': f'GAME DEFAULT ACTION: game stage 00 - Waiting'}), 200
    if game.stage == 1:
        if table.blind_game == 0:
            game.stage = 2
        elif table.blind_game == 1:
            player_index = game_players.index(game.speaker_id)
            new_usersays = get_string_array(game.usersays)  # Создаем копию массива
            new_usersays[player_index] = 'Without blind game'
            game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
            game.stage = 2
            db.session.commit()
        game.lastdeal = int(time.time())
        db.session.commit()
        socketio.emit('update_room', socket_data, to=socket_room)
        current_gamestage(game_id)
        return jsonify({'message': f'GAME DEFAULT ACTION: Game.stage is 01. New latdeal time is {game.lastdeal}'}), 200
    elif game.stage == 2:
        game.lastdeal = int(time.time())
        db.session.commit()
        socketio.emit('update_room', socket_data, to=socket_room)
        current_gamestage(game_id)
        return jsonify({'message': f'GAME DEFAULT ACTION: Game.stage is 03. New latdeal time is {game.lastdeal}'}), 200
    elif game.stage == 3:
        players_bet = get_array(game.players_bet)
        player_id = game.speaker_id
        if all(x == 0 for x in players_bet):
            if player_check(player_id, game_id):
                nextgamespeaker(game_id)
                check_checking(game_id)
                call_checking(game_id)
                fold_checking(game_id)
        else:
            if player_fold(player_id, game_id):
                nextgamespeaker(game_id)
                check_checking(game_id)
                call_checking(game_id)
                fold_checking(game_id)
        game.lastdeal = int(time.time())
        db.session.commit()
        socketio.emit('update_room', socket_data, to=socket_room)
        current_gamestage(game_id)
        return jsonify({'message': f'GAME DEFAULT ACTION: Game.stage is 02. New latdeal time is {game.lastdeal}'}), 200
    elif game.stage == 4:
        default_drop_card(game_id)
        game.lastdeal = int(time.time())
        db.session.commit()
        socketio.emit('update_room', socket_data, to=socket_room)
        current_gamestage(game_id)
        return jsonify({'message': f'GAME DEFAULT ACTION: Game.stage is 04. New latdeal time is {game.lastdeal}'}), 200
    elif game.stage == 5:
        default_turn_1(game_id)
        game.lastdeal = int(time.time())
        db.session.commit()
        socketio.emit('update_room', socket_data, to=socket_room)
        current_gamestage(game_id)
        return jsonify({'message': f'GAME DEFAULT ACTION: Game.stage is 05. New latdeal time is {game.lastdeal}'}), 200
    elif game.stage == 6:
        default_turn_2(game_id)
        game.lastdeal = int(time.time())
        db.session.commit()
        socketio.emit('update_room', socket_data, to=socket_room)
        current_gamestage(game_id)
        return jsonify({'message': f'GAME DEFAULT ACTION: Game.stage is 06. New latdeal time is {game.lastdeal}'}), 200
    elif game.stage == 7:
        default_turn_3(game_id)
        game.lastdeal = int(time.time())
        db.session.commit()
        socketio.emit('update_room', socket_data, to=socket_room)
        current_gamestage(game_id)
        return jsonify({'message': f'GAME DEFAULT ACTION: Game.stage is 07. New latdeal time is {game.lastdeal}'}), 200
    elif game.stage == 8:
        game.lastdeal = int(time.time())
        db.session.commit()
        socketio.emit('update_room', socket_data, to=socket_room)
        return jsonify({'message': f'GAME DEFAULT ACTION: Game.stage is 08. New latdeal time is {game.lastdeal}'}), 200
    elif game.stage == 9:
        default_azi_out(game_id)
        game.lastdeal = int(time.time())
        db.session.commit()
        socketio.emit('update_room', socket_data, to=socket_room)
        current_gamestage(game_id)
        return jsonify({'message': f'GAME DEFAULT ACTION: Game.stage is 09. New latdeal time is {game.lastdeal}'}), 200
    elif game.stage == 10:
        game.lastdeal = int(time.time())
        db.session.commit()
        socketio.emit('update_room', socket_data, to=socket_room)
        current_gamestage(game_id)
        return jsonify({'message': f'GAME DEFAULT ACTION: Game.stage is 10. New latdeal time is {game.lastdeal}'}), 200
    elif game.stage == 11 and count_players > 1:
        try:
            for i in range(0, 6):
                if table_players[i] != 0:
                    if game_players[i] == table_players[i] and game_status[i] != 1:
                        game_status[i] = 15
                    if game_players[i] == 0:
                        game_players[i] = table_players[i]
                        game.players = set_array(game_players)
                        game_status[i] = 16
            game.status = set_array(game_status)
            game.lastdeal = int(time.time())
            db.session.commit()
            socketio.emit('update_room', socket_data, to=socket_room)
            new_game_full(table_id)
            print(f'GAME DEFAULT ACTION: game stage 11 - Good')
            current_gamestage(game_id)
            return jsonify({'message': f'GAME DEFAULT ACTION: game stage 11 - Good'}), 200
        except:
            pass

    # game.lastdeal = int(time.time())
    # db.session.commit()
    # socketio.emit('update_room', socket_data, to=socket_room)
    # current_gamestage(game_id)
    # return jsonify({'message': f'Default action is done. New latdeal time is {game.lastdeal}'}), 200

def player_ready_for_new_game(player_id, table_id):
    try:
        table = Tables.query.get(table_id)
        game = Games.query.get(table.currentgame)
        table_players = get_array(table.players)
        non_zero_elements = [1 for element in table_players if element != 0]
        count_non_zero = non_zero_elements.count(1)
        if count_non_zero <= 1:
            return jsonify({'message': f'PLAYER {player_id} READY FOR NEW GAME: Player is alone'}), 208
        player_index = table_players.index(player_id)
        game_players = get_array(game.players)
        game_status = get_array(game.status)
        if (game.stage == 0) and (game_players[player_index] == 0):
            game_players[player_index] = player_id
            game.players = set_array(game_players)
            game_status[player_index] = 16
            game.status = set_array(game_status)
            db.session.commit()
            return jsonify({'message': f'User {player_id} is ready for game {game.id}'}), 200
        elif (game.stage == 11) and (game_players[player_index] == player_id):
            game_status[player_index] = 15
            game.status = set_array(game_status)
            db.session.commit()
            return jsonify({'message': f'User {player_id} is ready for next game'}), 200
        elif (game.stage == 11) and (game_players[player_index] == 0):
            game_players[player_index] = player_id
            game.players = set_array(game_players)
            game_status[player_index] = 16
            game.status = set_array(game_status)
            db.session.commit()
            return jsonify({'message': f'User {player_id} arrived and ready for next game'}), 200
        else:
            return jsonify({'message': f'Probably User {player_id} is already ready'}), 208
    except:
        return jsonify({'message': f'PLAYER {player_id} READY FOR NEW GAME: Error something wrong'}), 208

def ready_for_new_game_checking(table_id):
    try:
        table = Tables.query.get(table_id)
        game = Games.query.get(table.currentgame)
        table_players = get_array(table.players)
        game_players = get_array(game.players)
        game_status = get_array(game.status)
        all_players_ready = True
        players_count = 0
        for i in range(0, 6):
            if table_players[i] != 0:
                players_count += 1
                if table_players[i] != game_players[i]:
                    all_players_ready = False
                else:
                    if game_status[i] != 15 and game_status[i] != 16:
                        all_players_ready = False
        if all_players_ready and players_count > 1:
            if game.stage == 0:
                for i in range(0, 6):
                    game_status[i] = 0
                game.status = set_array(game_status)
                db.session.commit()
                print(f'CHECK READY NEW GAME at table {table_id} confirmed, this game is started!')
                return 1
            elif game.stage == 11:
                print(f'CHECK READY NEW GAME at table {table_id} confirmed, a new game is started!')
                return 2
            else:
                print(f'CHECK READY NEW GAME at table {table_id} confirmed, but ERROR!')
                return 3
    except:
        print(f'CHECK READY NEW GAME at table {table_id} failed!')
        return 4

def start_bet_all(game_id):
    game = Games.query.get(game_id)
    table = Tables.query.get(game.table_id)
    game_players = get_array(game.players)
    game_status = get_array(game.status)
    start_bets_are_off = True
    for i in range(0, 6):
        if (game_players[i] != 0) and (game_status[i] == 0):
            start_bets_are_off = False
    if start_bets_are_off:
        game.stage = 1
        db.session.commit()
        print('All bets are off')
    else:
        socket_room = 'table-' + str(table.id)
        socket_data = {'user_id': 0, 'room-id': socket_room}
        for p in range(0, 6):
            if game_players[p] !=0 and game_status[p] == 0:
                player = Players.query.get(game_players[p])
                if table.cointype == 0:
                    if player.freecoin >= table.min_bet:
                        player.freecoin -= table.min_bet
                        game.pot += table.min_bet
                        game_status[p] = 2
                        game.status = set_array(game_status)
                        new_usersays = get_string_array(game.usersays)  # Создаем копию массива
                        new_usersays[p] = 'Ante ' + text_number(table.min_bet)
                        game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
                        game.lastdeal = int(time.time())
                        db.session.commit()
                        print(f'User {player.id} | Player {player.nickname} betting ante {table.min_bet}')
                        socketio.emit('update_room', socket_data, to=socket_room)
                    else:
                        print(f'User {player.id} | Player {player.nickname} has not enough coin for playing')
                        game_status[p] = 1
                        game.status = set_array(game_status)
                        new_usersays = get_string_array(game.usersays)  # Создаем копию массива
                        new_usersays[p] = 'No funds to play'
                        game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
                        game.lastdeal = int(time.time())
                        db.session.commit()
                        socketio.emit('update_room', socket_data, to=socket_room)
                        check_poor_defeat(game_id)
                elif table.cointype == 1:
                    if player.goldcoin >= table.min_bet:
                        player.goldcoin -= table.min_bet
                        game.pot += table.min_bet
                        game_status[p] = 2
                        game.status = set_array(game_status)
                        new_usersays = get_string_array(game.usersays)  # Создаем копию массива
                        new_usersays[p] = 'Ante ' + text_number(table.min_bet)
                        game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
                        game.lastdeal = int(time.time())
                        db.session.commit()
                        print(f'User {player.id} | Player {player.nickname} betting ante {table.min_bet}')
                        socketio.emit('update_room', socket_data, to=socket_room)
                    else:
                        print(f'User {player.id} | Player {player.nickname} has not enough coin for playing')
                        game_status[p] = 1
                        game.status = set_array(game_status)
                        new_usersays = get_string_array(game.usersays)  # Создаем копию массива
                        new_usersays[p] = 'No funds to play'
                        game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
                        game.lastdeal = int(time.time())
                        db.session.commit()
                        socketio.emit('update_room', socket_data, to=socket_room)
                        check_poor_defeat(game_id)
                else:
                    pass

def start_rebet_all(game_id):
    game = Games.query.get(game_id)
    table = Tables.query.get(game.table_id)
    game_players = get_array(game.players)
    game_status = get_array(game.status)
    game_check = get_bool_array(game.check)
    start_rebets_are_off = True
    for i in range(0, 6):
        if game_players[i] != 0 and game_status[i] == 2 and game_check[i]:
            start_rebets_are_off = False

    if start_rebets_are_off:
        game.stage = 1
        db.session.commit()
        print(f'S_R_A: All re-bets are off, game.stage is {game.stage}')
        current_gamestage(game_id)
    else:
        game = Games.query.get(game_id)
        game_players = get_array(game.players)
        game_status = get_array(game.status)
        game_check = get_bool_array(game.check)
        print(f'START_REBET_ALL: ELIF GS ==10, GS is {game.stage} SRAO is {start_rebets_are_off},')
        socket_room = 'table-' + str(table.id)
        socket_data = {'user_id': 0, 'room-id': socket_room}
        for p in range(0, 6):
            print(f'GAMECHECK {p} = {game_check[p]}')
            if game_players[p] !=0 and game_status[p] == 2 and game_check[p]:
                print(f'GAMECHECK is really {p} = {game_check[p]}, GAME PLAYERS = {game_players}')
                print(f'CHECKING PLAYER ID : {game_players[p]} + 10 = {game_players[p] + 10}')
                player = Players.query.get(game_players[p])
                print(f'Player = {player}')
                if table.cointype == 0:
                    if player.freecoin >= table.min_bet:
                        print(f'IF INSIDE')
                        player.freecoin -= table.min_bet
                        game.pot += table.min_bet
                        game_status[p] = 2
                        game.status = set_array(game_status)
                        new_usersays = get_string_array(game.usersays)  # Создаем копию массива
                        new_usersays[p] = 'Add ante ' + text_number(table.min_bet)
                        game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
                        new_check = get_bool_array(game.check)
                        new_check[p] = False
                        game.check = set_bool_array(new_check)
                        game.lastdeal = int(time.time())
                        db.session.commit()
                        socketio.emit('update_room', socket_data, to=socket_room)
                        check_poor_defeat(game_id)
                    else:
                        print(f'Player {player.id} has not enough coin for playing')
                        game_status[p] = 1
                        game.status = set_array(game_status)
                        new_usersays = get_string_array(game.usersays)  # Создаем копию массива
                        new_usersays[p] = 'No funds to play'
                        game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
                        game.lastdeal = int(time.time())
                        db.session.commit()
                        socketio.emit('update_room', socket_data, to=socket_room)
                        check_poor_defeat(game_id)
                elif table.cointype == 1:
                    if player.goldcoin >= table.min_bet:
                        player.goldcoin -= table.min_bet
                        game.pot += table.min_bet
                        game_status[p] = 2
                        game.status = set_array(game_status)
                        new_usersays = get_string_array(game.usersays)  # Создаем копию массива
                        new_usersays[p] = 'Ante ' + text_number(table.min_bet)
                        game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
                        new_check = get_bool_array(game.check)
                        new_check[p] = False
                        game.check = set_bool_array(new_check)
                        game.lastdeal = int(time.time())
                        db.session.commit()
                        print(f'Player {player.id} added ante {table.min_bet}')
                        socketio.emit('update_room', socket_data, to=socket_room)
                        check_poor_defeat(game_id)
                    else:
                        print(f'Player {player.id} has not enough coin for playing')
                        game_status[p] = 1
                        game.status = set_array(game_status)
                        new_usersays = get_string_array(game.usersays)  # Создаем копию массива
                        new_usersays[p] = 'No funds to play'
                        game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
                        game.lastdeal = int(time.time())
                        db.session.commit()
                        socketio.emit('update_room', socket_data, to=socket_room)
                        check_poor_defeat(game_id)
                else:
                    pass
        game.stage = 1
        db.session.commit()
    current_gamestage(game_id)
def check_poor_defeat(game_id):
    game = Games.query.get(game_id)
    game_players = get_array(game.players)
    game_status = get_array(game.status)
    not_poor_players = 0
    winner_id = 0
    for i in range(0, 6):
        if (game_players[i] != 0) and (game_status[i] != 1):
            winner_id = game_players[i]
            not_poor_players += 1
    if not_poor_players != 1:
        return
    elif not_poor_players == 1:
        game.winner = game_players.index(winner_id) + 1
        player = Players.query.get(winner_id)
        table = Tables.query.get(game.table_id)
        table.dealing = game.winner
        game_status[game_players.index(winner_id)] = 9
        game.status = set_array(game_status)
        if table.cointype == 0:
            player.freecoin += game.pot
        elif table.cointype == 1:
            player.goldcoin += game.pot
        game.stage = 11
        game.end_game = datetime.utcnow()
        db.session.commit()
        print(f'POOR_END_GAME: Game {game_id} is over, {player.nickname} wins {game.pot}')
        socketio.emit('update_room', to='table-' + str(table.id))
        time.sleep(2)
        for i in range(0, 6):
            if game_status[i] == 1:
                drop_player(game_players[i], table.id)
                socketio.emit('update_room', to='table-' + str(table.id))
                socketio.emit('update_tables', to='tables')
        current_gamestage(game_id)

def default_drop_card(game_id):
    game = Games.query.get(game_id)
    game_players = get_array(game.players)
    card_players = get_array(game.card_players)
    game_status = get_array(game.status)
    for i in range(0, 6):
        if game_players[i] != 0 and game_status[i] == 2 and card_players[1 + (i * 4)] != 0:
            print(f'DEFAULT DROP CARD: player {game_players[i]} drops card {card_players[1 + (i * 4)]}')
            card_players[1 + (i * 4)] = 0
            game_status[i] = 6
    game.card_players = set_array(card_players)
    game.status = set_array(game_status)
    game.stage = 5
    db.session.commit()

def default_turn_1(game_id):
    game = Games.query.get(game_id)
    game_players = get_array(game.players)
    card_players = get_array(game.card_players)
    game_status = get_array(game.status)
    hodor_index = game.current_hodor - 1
    user_id = game_players[hodor_index]
    if game_status[hodor_index] == 6 and game_players[hodor_index] != 0:
        for i in range(0, 4):
            if card_players[game.current_hodor * 4 - i] != 0:
                card_id = card_players[game.current_hodor * 4 - i]
                if player_turn_1(game_id, user_id, card_id):
                    player_turn_1_checking(game_id)
                    break
    current_gamestage(game_id)

def default_turn_2(game_id):
    game = Games.query.get(game_id)
    game_players = get_array(game.players)
    card_players = get_array(game.card_players)
    game_status = get_array(game.status)
    hodor_index = game.current_hodor - 1
    user_id = game_players[hodor_index]
    if game_status[hodor_index] == 7 and game_players[hodor_index] != 0:
        for i in range(0, 4):
            if card_players[game.current_hodor * 4 - i] != 0:
                card_id = card_players[game.current_hodor * 4 - i]
                if player_turn_2(game_id, user_id, card_id):
                    player_turn_2_checking(game_id)
                    break
    current_gamestage(game_id)

def default_turn_3(game_id):
    game = Games.query.get(game_id)
    game_players = get_array(game.players)
    card_players = get_array(game.card_players)
    game_status = get_array(game.status)
    hodor_index = game.current_hodor - 1
    user_id = game_players[hodor_index]
    if game_status[hodor_index] == 8 and game_players[hodor_index] != 0:
        for i in range(0, 4):
            if card_players[game.current_hodor * 4 - i] != 0:
                card_id = card_players[game.current_hodor * 4 - i]
                if player_turn_3(game_id, user_id, card_id):
                    player_turn_3_checking(game_id)
                    break
    current_gamestage(game_id)

def default_azi_out(game_id):
    game = Games.query.get(game_id)
    game_players = get_array(game.players)
    game_status = get_array(game.status)
    for i in range(0, 6):
        if game_status[i] == 12:
            player_azi_out(game_id, game_players[i])
    player_azi_in_checking(game_id)
