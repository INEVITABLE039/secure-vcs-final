import sqlite3
import logging
import re
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Logging setup
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()
@app.route('/', methods=['GET'])
def home():
    return '''
        <h2>Welcome to the Secure Virtual Collaboration Platform</h2>
        <p><a href="/login">Login</a> | <a href="/register">Register</a></p>
    '''

def is_valid_username(username):
    return bool(re.match(r'^[a-zA-Z0-9_]{5,20}$', username))

def is_valid_password(password):
    return bool(len(password) >= 8 and re.search(r'[A-Za-z]', password) and re.search(r'[0-9]', password))

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not is_valid_username(username) or not is_valid_password(password):
        logging.warning(f"Invalid registration attempt: {username}")
        return jsonify({'message': 'Invalid username or password'}), 400

    hashed_password = generate_password_hash(password)
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        logging.info(f"New user registered: {username}")
        return jsonify({'message': 'Registration successful'}), 201
    except sqlite3.IntegrityError:
        logging.warning(f"Username already exists: {username}")
        return jsonify({'message': 'Username already exists'}), 409
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()

    if result and check_password_hash(result[0], password):
        logging.info(f"Successful login: {username}")
        return jsonify({'message': 'Login successful'}), 200
    else:
        logging.warning(f"Failed login attempt: {username}")
        return jsonify({'message': 'Invalid credentials'}), 401
@app.route('/login', methods=['GET'])
def login_form():
    return '''
        <form method="POST" action="/login">
            <input name="username" placeholder="Username" />
            <input name="password" placeholder="Password" type="password" />
            <button type="submit">Login</button>
        </form>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

