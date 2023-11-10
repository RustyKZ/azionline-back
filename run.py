from app import app, socketio
from app.gaming import *

if __name__ == '__main__':
    # app.run(host="0.0.0.0", port=8000)
    # socketio.run(app, port=8000, allow_unsafe_werkzeug = True)
    app.run(debug=True, port=8000)

# if __name__ == '__main__':
#     with app.app_context():
#         table_id = 1  # Замените на нужный вам ID стола
#         start_new_game(create_new_game(table_id))