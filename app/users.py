from app import *
from flask import jsonify, request, redirect
from app.classes import *
from eth_account import Account
from eth_account.messages import encode_defunct
from datetime import datetime

def user_checking(email, nickname):
    existing_user_by_email = Players.query.filter_by(email=email).first()
    existing_user_by_nickname = Players.query.filter_by(nickname=nickname).first()

    if existing_user_by_email:
        return jsonify({'message': 'User with this email already exists'}), 400

    if existing_user_by_nickname:
        return jsonify({'message': 'User with this nickname already exists'}), 400

    return None  # Нет существующих пользователей с таким email и nickname

def user_register(data):
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    # Провести проверку email и nickname
    check_result = user_checking(email, name)
    if check_result:
        return check_result
    # Хеширование пароля
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    # Создание нового пользователя
    new_user = Players(
        nickname=name,
        password=hashed_password,
        email=email,
        freecoin=1000,
        goldcoin=0,
        ip_address=request.remote_addr,
        reg_date=datetime.utcnow(),
        active_table=0,
        reputation=0,
        rating=1000,
        wallet='',
        game_status=0,
        public_key='',
        airdropfree = 1000,
    )
    db.session.add(new_user)
    db.session.commit()
    print(name + ' ' + email + ' registered!')
    return jsonify({'message': 'User registered successfully'}), 200  # Отправляем JSON с сообщением об успешной регистрации

def user_login(data):
    print(f'USER LOGIN {data}')
    email = data.get('email')
    password = data.get('password')

    user = Players.query.filter_by(email=email).first()
    if not user:
        print('User not found')
        return jsonify({'message': 'User not found'}), 401

    if bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        print(user.nickname + ' logged in!')
        return jsonify(access_token=access_token)
    else:
        print('Invalid password')
        return jsonify({'message': 'Invalid password'}), 401


def verify_signature(user_address, signature, message):
    print('data_to_sign', message)
    try:
        # Проверяем подпись
        recovered_address = Account.recover_message(encode_defunct(text=message), signature=signature)
        print('Recovered address: ', recovered_address)
        if recovered_address.lower() == user_address.lower():
            print('YEAH!!!!!')
        return True
    except Exception as e:
        pass
    return False

def user_wallet_register(data):
    if not data:
        return jsonify({'message': 'Invalid data'}), 400
    user_address = data.get('userAddress')
    user_signature = data.get('signature')
    message = '"User address: ' + user_address + '"'
    print('user_address = ', user_address, ' Signature = ', user_signature)
    if verify_signature(user_address, user_signature, message):
        print('Signature good')
        # Проверяем наличие пользователя в таблице 'players'
        user = Players.query.filter_by(wallet=user_address).first()
        # Преобразуйте байтовый объект в строку для сохранения в базе данных или других операций
        if not user:
            # Создаем нового пользователя, если его нет в базе данных
            new_user = Players(
                nickname=user_address,
                password='',
                email='',
                freecoin=1000,
                goldcoin=0,
                ip_address=request.remote_addr,
                reg_date=datetime.utcnow(),
                active_table=0,
                reputation=0,
                rating=1000,
                wallet=user_address,
                game_status=0,
                public_key='',
                airdropfree=1000,
            )
            db.session.add(new_user)
            db.session.commit()
            # Перенаправляем пользователя на страницу профиля с именем пользователя
            return jsonify({'message': 'User registered successfully, need to change nickname','nick':'bad'}), 200  # Отправляем JSON с сообщением об успешной регистрации

        elif user.wallet == user.nickname or user.nickname == '':
            # Если пользователь с таким кошельком и именем существует, перенаправляем на его профиль
            return jsonify({'message': 'User is already registered, need to change nickname', 'nick':'bad'}), 200  # Отправляем JSON с сообщением об успешной регистрации

        else:
            # Если пользователь с таким кошельком и другим именем существует, вернем пользователя на предыдущую страницу
            return jsonify({'message': 'User logged successfully', 'nick':'good'}), 200  # Отправляем JSON с сообщением об успешной регистрации
    else:
        print('Signature bad')
        return jsonify({'message': 'Signature bad'}), 400

def user_email_wallet(data, current_user_id):
    if not data:
        return jsonify({'message': 'Invalid data'}), 400
    user_address = data.get('userAddress')
    user_id_str = data.get('userId')
    try:
        user_id = int(user_id_str)
    except ValueError:
        user_id = None
    if user_id != current_user_id:
        print('Server authorization is not confirmed! User address client is: ', user_id, 'User address server is: ', current_user_id)
        return jsonify({'message': 'Server authorization is not confirmed!'}), 401
    user_signature = data.get('signature')
    message = '"Do you want to link your account to your wallet ' + user_address + ' ?"'
    print('user_address = ', user_address, ' Signature = ', user_signature)
    print('Message for signature: ', message)
    if verify_signature(user_address, user_signature, message):
        print('Signature good')
        # Проверяем наличие пользователя в таблице 'players'
        user = Players.query.filter_by(id=current_user_id).first()
        user_with_wallet = Players.query.filter_by(wallet=user_address).first()
        if user_with_wallet:
            if user_with_wallet.wallet == user_address and user_with_wallet.id != user.id:
                print('This wallet address already linked to another account!'), 401
                return jsonify({'message': 'This account already have linked wallet!'}), 401
        if user.wallet == user_address:
            print('This account already have linked wallet!')
            return jsonify({'message': 'User logged into account successfully'}), 200
        elif user.wallet == '':
            user.wallet = user_address
            db.session.commit()
            print('User wallet added into database...')
            return jsonify({'message': 'User wallet linked to account successfully'}), 200
        else:
            print('This account already have linked wallet!')
            return jsonify({'message': 'This account already have linked wallet!'}), 401

    else:
        print('Signature bad')
        return jsonify({'message': 'Signature bad'}), 400


def get_user_profile(user_id, data):
    current_user_id = data.get('user_id')
    user = Players.query.filter_by(id=user_id).first()
    if not user:
        print(f'User {user_id} not found')
        return jsonify({'message': 'User not found'}), 401
    if user_id == current_user_id:
        userinfo = {
            'id': user.id,
            'nickname': user.nickname,
            'email': user.email,
            'freecoin': user.freecoin,
            'goldcoin': user.goldcoin,
            'ip_address': user.ip_address,
            'reg_date': user.reg_date.strftime('%Y-%m-%d %H:%M:%S'),  # Преобразование даты в строку
            'active_table': user.active_table,
            'reputation': user.reputation,
            'rating': user.rating,
            'wallet': user.wallet
        }
        return jsonify({'message': 'User seflinfo sended'}, userinfo), 200
    else:
        userinfo = {
            'id': user.id,
            'nickname': user.nickname,
            'email': None,
            'freecoin': None,
            'goldcoin': None,
            'ip_address': None,
            'reg_date': user.reg_date.strftime('%Y-%m-%d %H:%M:%S'),  # Преобразование даты в строку
            'active_table': user.active_table,
            'reputation': user.reputation,
            'rating': user.rating,
            'wallet': None
        }
        return jsonify({'message': 'Userinfo sended'}, userinfo), 200

def change_user_name(data):
    user_id_str = data.get('user_id')
    editor_id_str = data.get('editor_id')
    try:
        user_id = int(user_id_str)
        editor_id = int(editor_id_str)
    except ValueError:
        user_id = None
        return jsonify({'message': 'User not found'}), 401
    user = Players.query.filter_by(id=user_id).first()
    new_name = data.get('new_name')
    if not user or not new_name:
        return jsonify({'message': 'User not found'}), 401
    twin_user = Players.query.filter_by(nickname=new_name).first()
    if twin_user:
        return jsonify({'message': 'This nickname already registered'}), 401
    elif user_id != editor_id:
        return jsonify({'message': 'You can not change not your nickname'}), 403
    else:
        user.nickname = new_name
        db.session.commit()
        return jsonify({'message': 'User nickname renamed successfully'}), 200


