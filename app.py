# Necessary libraries and packages are imported
from flask import Flask, render_template, request, redirect, url_for, session, Response
import sqlite3
import json
from datetime import date
import io

app = Flask(__name__)
# Defines the secret key for each session
app.secret_key = 'secret_key'

# Define database path
DB_path = 'D:\Programming Projects\Smart-Finance\database.db'

#Initialises the users table
def init_db_users():
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Retrieves all user records in the database
def get_all_users():
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute('SELECT username, password FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

# Retrieves the username of each user in the database
def get_all_usernames():
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users')
    usernames = cursor.fetchall()
    conn.commit()
    conn.close()
    return usernames

# Adds a user to the users table
def add_user(username, password):
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

# Validates the inputted username
def username_validation(username):
    usernames = get_all_usernames()
    if not username or username.isspace():
        return "Username must not be empty or just whitespace"
    elif len(username) < 3:
        return "Username is too short"
    elif len(username) > 20:
        return "Username is too long"
    elif (username,) in usernames:
        return 'Username already taken'
    else:
        return ''

# Validates the inputted password
def password_validation(password):
    if not password or password.isspace():
        return "Password must not be empty or just whitespace"
    elif len(password) < 12:
        return "Password is too short"
    elif password == password.lower():
        return "Password must contain at least one capital letter"
    else:
        return ''

# Validates username and password and returns appropriate feedback to frontend
def validation(username, password):
    if username_validation(username) or password_validation(password):
        return f'["{username_validation(username)}", "{password_validation(password)}"]'
    else:
        return '["successful"]'

@app.route('/registration')
@app.route('/registration.html')
def registration():
    return render_template('registration.html')

@app.route('/login')
@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/add_user', methods=['GET', 'POST'])
def add_user_route():
    if request.method == 'POST':
        # Retrieves the entered username and password
        username = request.form.get('username')
        password = request.form.get('password')
        result = validation(username, password)
        if result == '["successful"]':
            # Adds the new user to the users table if they have passed validation
            add_user(username, password)
        return result
    else:
        return redirect(url_for('index_page'))

@app.route('/verify_user', methods=['GET', 'POST'])
def verify_user_route():
    if request.method == 'POST':
        # Retrieves the entered username and password
        username = request.form.get('username')
        password = request.form.get('password')
        users = get_all_users()
        if (username, password) in users:
            # This is so that once the user is logged in, their username can always be accessed
            session['username'] = username
            return '["/index.html"]'
        else:
            return '["No matching account found", 1]'
    else:
        return redirect(url_for('index_page'))

if __name__ == "__main__":
    init_db_users()

    app.run(debug=True)