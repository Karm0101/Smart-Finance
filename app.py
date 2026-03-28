from flask import Flask, render_template, request, redirect, url_for, session, Response
import sqlite3
import json
from datetime import date
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

app = Flask(__name__)
app.secret_key = 'secret_key'

DB_path = 'D:\Programming Projects\Smart-Finance---Prototype\prototype.db'

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

def get_all_users():
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute('SELECT username, password FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

def get_all_usernames():
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users')
    usernames = cursor.fetchall()
    conn.commit()
    conn.close()
    return usernames

def add_user(username, password):
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

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

def password_validation(password):
    if not password or password.isspace():
        return "Password must not be empty or just whitespace"
    elif len(password) < 12:
        return "Password is too short"
    elif password == password.lower():
        return "Password must contain at least one capital letter"
    else:
        return ''

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
        username = request.form.get('username')
        password = request.form.get('password')
        result = validation(username, password)
        if result == '["successful"]':
            add_user(username, password)
        return result
    else:
        return redirect(url_for('index_page'))

@app.route('/verify_user', methods=['GET', 'POST'])
def verify_user_route():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users = get_all_users()
        if (username, password) in users:
            session['username'] = username
            return '["/index.html"]'
        else:
            return '["No matching account found", 1]'
    else:
        return redirect(url_for('index_page'))

if __name__ == "__main__":
    init_db_users()
    init_db_monthly_budgets()
    init_db_debts()
    init_db_spending()
    init_db_goals()
    init_db_forecasts()
    init_db_forecast_goals()
    init_db_forecast_categories()

    app.run(debug=True)