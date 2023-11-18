import os
from app import *
from flask import render_template, jsonify, request, redirect, url_for
from app.classes import *
from app.users import *
from sqlalchemy import desc
from app.gaming import *
from math import floor
# from app.config import CLIENT_URL
from eth_account.messages import defunct_hash_message
import traceback


@app.route('/API/getarticles')
def get_articles():
    posts = Articles.query.order_by(desc(Articles.id)).all()
    data = []
    for post in posts:
        post_data = {
            'id': post.id,
            'title': post.Title,
            'subtitle': post.SubTitle,
            'text': post.Text,
            # 'publication_date': post.PublicationDate.strftime('%Y-%m-%d') if post.PublicationDate else None,  # Преобразуем дату в строку, если нужно
            'publication_date': post.PublicationDate.strftime('%Y-%b-%d') if post.PublicationDate else None,
            'image': post.Image
        }
        data.append(post_data)
    return jsonify(data)

# @app.route('/API/addpost', methods=['POST'])
# def add_post():
#     if request.method == 'POST':
#         # Запрос последней записи из таблицы Articles
#         last_article = Articles.query.order_by(Articles.id.desc()).first()
#         # Получаем id последней записи
#         last_id = last_article.id if last_article else 0  # Проверяем, есть ли записи в таблице
#         # Генерируем имя изображения с использованием last_id
#         image_name = f'post{last_id + 1}.jpg'
#         title = request.form['title']
#         subtitle = request.form['subTitle']
#         text = request.form['text']
#         # if 'image' in request.files:
#         #     image = request.files['image']
#         #     image_path = os.path.join(app.config['UPLOADED_IMAGES_DEST'], image_name)
#         #     image.save(image_path)  # Сохраняем изображение
#         new_article = Articles(Title=title, SubTitle=subtitle, Text=text, Image=image_name)
#         db.session.add(new_article)
#         db.session.commit()
#     return jsonify({'message': 'Post added successfully'})
#
#
# @app.route('/API/delete/<int:post_id>', methods=['DELETE'])
# def delete_post(post_id):
#     try:
#         # Найдем статью по указанному post_id
#         post = Articles.query.get(post_id)
#         if post:
#             # Если статья существует, удалим ее из базы данных
#             db.session.delete(post)
#             db.session.commit()
#             return jsonify({'message': 'Post deleted successfully'})
#         else:
#             # Если статья не найдена, вернем ошибку 404 (Not Found)
#             return jsonify({'error': 'Post not found'}), 404
#     except Exception as e:
#         # В случае любых ошибок при удалении, вернем ошибку 500 (Internal Server Error)
#         return jsonify({'error': str(e)}), 500


@app.route('/API/adduser', methods=['POST', 'GET'])
def add_user():
    data = request.get_json()  # Получите данные из JSON запроса
    if not data:
        return jsonify({'message': 'Invalid data'}), 400

    result = user_register(data)  # Вызов функции для регистрации пользователя

    return result

@app.route('/API/login', methods=['POST','GET'])
def login():
    data = request.get_json()
    if not data:
        print('bad data: ', data)
        return jsonify({'message': 'Invalid data'}), 400
    result = user_login(data)
    return result

@app.route('/API/logout', methods=['POST', 'GET'])
def logout():
    print('User logged out')
    return jsonify({'message': 'Logged out successfully'})

@app.route('/API/check_auth', methods=['GET', 'POST'])
@jwt_required()  # Только авторизованным пользователям разрешен доступ
def check_auth():
    print('CHECK AUTH')
    current_user_id = 0
    active_table = 0
    try:
        current_user_id = get_jwt_identity()
        current_user = Players.query.filter_by(id=current_user_id).first()
        active_table = current_user.active_table
    except:
        pass
    # Создайте словарь имен пользователей
    users = Players.query.all()
    users_info = {}
    for user in users:
        users_info[user.id] = user.nickname
    print(f'CHECK AUTH: User {current_user_id} is authenticated, User Table : {active_table}')
    return jsonify({'authenticated': True, 'user_id': current_user_id, 'users_info': users_info, 'user_table': active_table})

@app.route('/API/wallet_connect', methods=['GET', 'POST'])
def wallet_connect():
    data = request.get_json()  # Получите данные из JSON запроса
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    result = user_wallet_register(data)  # Вызов функции для регистрации пользователя
    return result

@app.route('/API/wallet_email_connect', methods=['GET', 'POST'])
@jwt_required()  # Только авторизованным пользователям разрешен доступ
def wallet_email_connect():
    data = request.get_json()  # Получите данные из JSON запроса
    current_user_id = get_jwt_identity()
    print('User ', current_user_id, ' wants to link Metamask')
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    result = user_email_wallet(data, current_user_id)  # Вызов функции для регистрации пользователя
    return result

@app.route('/API/check_web3_auth', methods=['GET', 'POST'])
def check_web3_auth():
    data = request.get_json()
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    user_address = data.get('userWallet')
    user = Players.query.filter_by(wallet=user_address).first()
    current_user_id = user.id
    if not user:
        print('User ' + user_address + ' not found')
        return jsonify({'message': 'User not found'}), 401
    users = Players.query.all()
    users_info = {}
    for us in users:
        users_info[us.id] = us.nickname
    return jsonify({'web3auth': True, 'user_id': current_user_id, 'users_info': users_info, 'user_table': user.active_table})

@app.route('/API/profile/<int:user_id>', methods=['POST', 'GET'])
def get_profile(user_id):
    data = request.get_json()
    print(f'/API/profile/: user_ID is {user_id} Data is {data}')
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    result = get_user_profile(user_id, data)
    return result

@app.route('/API/change_name', methods=['POST', 'GET'])
def change_name():
    data = request.get_json()
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    result = change_user_name(data)
    return result

@app.route('/API/tables', methods=['POST'])
def tables():
    data = request.get_json()
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    user_id = data.get('user_id')
    result = get_tables(user_id)
    return result

@app.route('/API/join_table', methods=['POST'])
def join_table():
    data = request.get_json()
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    print(data)
    result = game_join_table(data)
    return result

@app.route('/API/leave_table', methods=['POST'])
def leave_table():
    data = request.get_json()
    print('/API/leave_table: ', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    result = game_leave_table(data)
    return result

@app.route('/API/get_table', methods=['POST'])
def get_table():
    data = request.get_json()
    print('/API/get_table: ', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    result = game_get_table(data)
    return result

@app.route('/API/new_game', methods=['POST'])
def new_game():
    data = request.get_json()
    print('API/new_game/', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    table_id = data.get('table_id')
    new_game_full(table_id)
    socketio.emit('update_room', data, to='table-'+str(table_id))
    return jsonify({'message': f'New game started on table ${table_id}'}), 200

@app.route('/API/new_speaker', methods=['POST'])
def new_speaker():
    data = request.get_json()
    print('API/new_speaker/', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    game_id = data.get('game_id')
    table_id = data.get('table_id')
    current_speaker = data.get('current_speaker')
    table = Tables.query.filter_by(id=table_id).first()
    game = Games.query.filter_by(id=game_id).first()
    current_time = int(time.time())
    if (current_speaker) == game.speaker_id and (current_time >= game.lastdeal + table.interval):
        nextgamespeaker(game_id)
        socketio.emit('update_room', data, to='table-'+str(table_id))
        return jsonify({'message': f'New speaker is {game.speaker_id}'}), 200

@app.route('/API/betting', methods=['POST'])
def betting():
    data = request.get_json()
    print('API/betting/', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    user_id = data.get('user_id')
    game_id = data.get('game_id')
    bet = data.get('bet')
    if player_bet(user_id, game_id, bet):
        nextgamespeaker(game_id)
        return jsonify({'message': f'Player {user_id} bets {bet} in game {game_id}'}), 200

@app.route('/API/calling', methods=['POST'])
def calling():
    data = request.get_json()
    print('API/calling/', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    user_id = data.get('user_id')
    game_id = data.get('game_id')
    bet = data.get('bet')
    if player_call(user_id, game_id):
        nextgamespeaker(game_id)
        call_checking(game_id)
        return jsonify({'message': f'Player {user_id} call {bet} in game {game_id}'}), 200

@app.route('/API/raising', methods=['POST'])
def raising():
    data = request.get_json()
    print('API/raising/', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    user_id = data.get('user_id')
    game_id = data.get('game_id')
    bet = data.get('bet')
    if player_raise(user_id, game_id, bet):
        nextgamespeaker(game_id)
        return jsonify({'message': f'Player {user_id} raise {bet} in game {game_id}'}), 200

@app.route('/API/check', methods=['POST'])
def check():
    data = request.get_json()
    print('API/check/', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    user_id = data.get('user_id')
    game_id = data.get('game_id')
    if player_check(user_id, game_id):
        nextgamespeaker(game_id)
        check_checking(game_id)
        call_checking(game_id)
        fold_checking(game_id)
        return jsonify({'message': f'Player {user_id} check in game {game_id}'}), 200
    else:
        return jsonify({'message': f'Player {user_id} not check in game {game_id}'}), 200

@app.route('/API/fold', methods=['POST'])
def fold():
    data = request.get_json()
    print('API/fold/', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    user_id = data.get('user_id')
    game_id = data.get('game_id')
    if player_fold(user_id, game_id):
        nextgamespeaker(game_id)
        check_checking(game_id)
        call_checking(game_id)
        fold_checking(game_id)
        return jsonify({'message': f'Player {user_id} fold in game {game_id}'}), 200
    else:
        return jsonify({'message': f'Player {user_id} trying to fold game {game_id} but smth wrong'}), 401

@app.route('/API/drop_extra_card', methods=['POST'])
def drop_extra_card():
    data = request.get_json()
    print('API/drop_extra_card/', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    user_id = data.get('user_id')
    game_id = data.get('game_id')
    card_id = data.get('card_value')
    if player_drop_extra_card(game_id, user_id, card_id):
        player_drop_extra_card_checking(game_id)
        return jsonify({'message': f'Player {user_id} dropped card {card_id} in game {game_id}'}), 200
    else:
        return jsonify({'message': f'Player {user_id} trying to drop card {card_id} in game {game_id} but smth wrong'}), 401

@app.route('/API/turn_1', methods=['POST'])
def turn_1():
    data = request.get_json()
    print('/API/turn_1', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    user_id = data.get('user_id')
    game_id = data.get('game_id')
    card_id = data.get('card_value')
    if player_turn_1(game_id, user_id, card_id):
        player_turn_1_checking(game_id)
        return jsonify({'message': f'Player {user_id} turn #1 card {card_id} in game {game_id}'}), 200
    else:
        return jsonify({'message': f'Player {user_id} trying to turn #1 card {card_id} in game {game_id} but smth wrong'}), 401

@app.route('/API/turn_2', methods=['POST'])
def turn_2():
    data = request.get_json()
    print('/API/turn_2', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    user_id = data.get('user_id')
    game_id = data.get('game_id')
    card_id = data.get('card_value')
    if player_turn_2(game_id, user_id, card_id):
        player_turn_2_checking(game_id)
        return jsonify({'message': f'Player {user_id} turn #2 card {card_id} in game {game_id}'}), 200
    else:
        return jsonify({'message': f'Player {user_id} trying to turn #2 card {card_id} in game {game_id} but smth wrong'}), 401

@app.route('/API/turn_3', methods=['POST'])
def turn_3():
    data = request.get_json()
    print('/API/turn_3', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    user_id = data.get('user_id')
    game_id = data.get('game_id')
    card_id = data.get('card_value')
    if player_turn_3(game_id, user_id, card_id):
        player_turn_3_checking(game_id)
        return jsonify({'message': f'Player {user_id} turn #3 card {card_id} in game {game_id}'}), 200
    else:
        return jsonify({'message': f'Player {user_id} trying to turn #3 card {card_id} in game {game_id} but smth wrong'}), 401

@app.route('/API/azi_in', methods=['POST'])
def azi_in():
    data = request.get_json()
    print('/API/azi_in', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    user_id = data.get('user_id')
    game_id = data.get('game_id')
    if player_azi_in(game_id, user_id):
        player_azi_in_checking(game_id)
        return jsonify({'message': f'Player {user_id} joining into AZI in game {game_id}'}), 200
    else:
        return jsonify({'message': f'Player {user_id} trying to join into AZI in game {game_id} but smth wrong'}), 401

@app.route('/API/azi_out', methods=['POST'])
def azi_out():
    data = request.get_json()
    print('/API/azi_out', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    user_id = data.get('user_id')
    game_id = data.get('game_id')
    if player_azi_out(game_id, user_id):
        player_azi_in_checking(game_id)
        return jsonify({'message': f'Player {user_id} refuse to join into AZI in game {game_id}'}), 200
    else:
        return jsonify({'message': f'Player {user_id} trying to refuse to join into AZI {game_id} but smth wrong'}), 401

@app.route('/API/blind', methods=['POST'])
def blind():
    data = request.get_json()
    print('API/blind/', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    user_id = data.get('user_id')
    game_id = data.get('game_id')
    bet = data.get('bet')
    if player_blind(user_id, game_id, bet):
        nextgamespeaker(game_id)
        current_gamestage(game_id)
        return jsonify({'message': f'Player {user_id} bets blind {bet * 2} in game {game_id}'}), 200

@app.route('/API/blind_check', methods=['POST'])
def blind_check():
    data = request.get_json()
    print('API/blind_check/', data)
    try:
        print('API/blind_check/ - in try')
        game_id = data.get('game_id')
        user_id = int(data.get('user_id'))
        game = Games.query.get(game_id)
        game_players = get_array(game.players)
        player_index = game_players.index(user_id)
        new_usersays = get_string_array(game.usersays)  # Создаем копию массива
        new_usersays[player_index] = 'Without blind game'
        game.usersays = set_string_array(new_usersays)  # Присваиваем копию обратно)
        game.stage = 2
        game.lastdeal = int(time.time())
        db.session.commit()
        current_gamestage(game_id)
        return jsonify({'message': f'Player {user_id} without blind in game {game_id}'}), 200
    except:
        print('API/blind_check/ - except')
        return jsonify({'message': 'Invalid data'}), 400

@app.route('/API/get_404', methods=['POST'])
def get_404():
    data = request.get_json()
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    user_id = data.get('user_id')
    result = get_404_page(user_id)
    return result

@app.route('/API/create_table', methods=['POST'])
def create_teble():
    data = request.get_json()
    print('API/create_table', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    result = create_new_table(data)
    return result

@app.route('/API/default_action', methods=['POST'])
def default_action():
    data = request.get_json()
    print('API/default_action/', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    # try:
    else:
        game_id = data.get('game_id')
        table_id = data.get('table_id')
        user_id = data.get('user_id')
        table = Tables.query.filter_by(id=table_id).first()
        game = Games.query.filter_by(id=game_id).first()
        current_time = int(time.time())
        socket_room = 'table-'+str(table_id)
        socket_data = {'user_id': 0, 'room-id': socket_room}
        if (current_time >= game.lastdeal + table.interval):
            result = game_default_action(table_id, game_id, user_id)
            # game.lastdeal = int(time.time())
            # db.session.commit()
            # socketio.emit('update_room', socket_data, to=socket_room)
            return result

            # return jsonify({'message': f'Default action is not running. Timer updated'}), 200
        else:
            # socketio.emit('update_room', socket_data, to=socket_room)
            return jsonify({'message': f'Default action is not running. It is too early for running it'}), 200
    # except:
    #     print('DEFAULT ACTION EXCEPT 206')
    #     return jsonify({'message': f'Default action is running. Incorrect response'}), 206

@app.route('/API/ready_for_new_game', methods=['POST'])
def ready_for_new_game():
    data = request.get_json()
    print('API/ready_for_new_game/', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    table_id = data.get('table_id')
    user_id = data.get('user_id')
    result = player_ready_for_new_game(user_id, table_id)
    table = Tables.query.get(table_id)
    game = Games.query.get(table.currentgame)
    ready_status = ready_for_new_game_checking(table_id)
    if ready_status == 1:
        start_new_game(game.id)
        current_gamestage(game.id)
    elif ready_status == 2:
        new_game_full(table_id)
    elif ready_status == 3:
        print('/API/ready_for_new_game: ERROR 3')
    elif ready_status == 4:
        print('/API/ready_for_new_game: ERROR 4')
    return result

@app.route('/API/getrules')
def get_rules():
    posts = Rules.query.order_by(Rules.id).all()
    data = []
    for post in posts:
        post_data = {
            'id': post.id,
            'title': post.Title,
            'subtitle': post.SubTitle,
            'text': post.Text,
            'image': post.Image
        }
        data.append(post_data)
    return jsonify(data)

@app.route('/API/getabout')
def get_about():
    posts = About.query.order_by(About.id).all()
    data = []
    for post in posts:
        post_data = {
            'id': post.id,
            'title': post.Title,
            'subtitle': post.SubTitle,
            'text': post.Text,
            'image': post.Image
        }
        data.append(post_data)
    return jsonify(data)

@app.route('/API/add_goldcoin', methods=['POST'])
def get_goldcoin():
    data = request.get_json()
    print('API/add_golcoin/', data)
    if not data:
        print('Invalid data')
        return jsonify({'message': 'Invalid data'}), 400
    try:
        user_id = data.get('user_id')
        goldcoin_quantity = data.get('gold')
        player = Players.query.get(user_id)
        player.goldcoin += goldcoin_quantity
        player.depositgold += goldcoin_quantity
        new_transaction = Transactions(user_id=user_id, goldcoin=goldcoin_quantity)
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({'message': f'User {user_id} successfully topped up his account with {goldcoin_quantity} goldcoin'}), 200
    except:
        return jsonify({'message': 'Something went wrong'}), 400

@app.route('/API/gettoplist')
def get_toplist():
    players = Players.query.all()
    data = []
    for player in players:
        freegain = player.freecoin - player.depositfree - player.airdropfree
        goldgain = player.goldcoin - player.depositgold - player.airdropgold
        reg_date = player.reg_date
        current_time = datetime.utcnow()
        time_difference = current_time - reg_date
        gamedays = floor(time_difference.total_seconds() / (60 * 60 * 24))
        post_data = {
            'id': player.id,
            'nickname': player.nickname,
            'freegain': freegain,
            'goldgain': goldgain,
            'date': gamedays,
            'rating': player.rating,
            'reputation': player.reputation
        }
        data.append(post_data)
    return jsonify(data)



