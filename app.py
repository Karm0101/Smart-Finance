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

# Initialises the users table
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

# Initialises the monthly_budgets table
def init_db_monthly_budgets():
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monthly_budgets (
            budget_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            month_year TEXT NOT NULL,
            income REAL NOT NULL,
            spending_added_date TEXT NOT NULL,
            FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

# Initialises the debts table
def init_db_debts():
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS debts (
            debt_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            debt_name TEXT NOT NULL,
            debt_amount REAL NOT NULL,
            interest_rate REAL NOT NULL,
            FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

# Initialises the spending table
def init_db_spending():
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spending (
            spending_id INTEGER PRIMARY KEY,
            budget_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY(budget_id) REFERENCES monthly_budgets(budget_id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

# Initialises the goals table
def init_db_goals():
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            goal_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            deadline TEXT NOT NULL,
            goal_name TEXT NOT NULL,
            goal_amount REAL NOT NULL,
            FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

# Initialises the forecasts table
def init_db_forecasts():
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forecasts (
            forecast_id INTEGER PRIMARY KEY,
            budget_id INTEGER NOT NULL,
            created_date TEXT NOT NULL,
            spending_cap REAL NOT NULL,
            FOREIGN KEY(budget_id) REFERENCES monthly_budgets(budget_id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

# Initialises the forecast_goals table
def init_db_forecast_goals():
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forecast_goals (
            forecast_goal_id INTEGER PRIMARY KEY,
            forecast_id INTEGER NOT NULL,
            goal_name TEXT NOT NULL,
            goal_amount REAL NOT NULL,
            FOREIGN KEY(forecast_id) REFERENCES forecasts(forecast_id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

# Initialises the forecast_categories table
def init_db_forecast_categories():
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forecast_categories (
            forecast_category_id INTEGER PRIMARY KEY,
            forecast_id INTEGER NOT NULL,
            category_name TEXT NOT NULL,
            forecast_amount REAL NOT NULL,
            FOREIGN KEY(forecast_id) REFERENCES forecasts(forecast_id) ON DELETE CASCADE
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

# Adds a monthly budget to the monthly_budgets table
def add_monthly_budget(income, month_year):
    username = session['username']
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    # Retrieves the username and month_year of all submitted spending forms
    cursor.execute('SELECT username, month_year FROM monthly_budgets')
    budget_records = cursor.fetchall()
    # If there already is a submitted spending form for the current month, it is replaced by the new one
    if (username, month_year) in budget_records:
        # Deletes the old budget form for the current month
        cursor.execute(f'DELETE FROM monthly_budgets WHERE username="{username}" AND month_year="{month_year}"')
    cursor.execute('INSERT INTO monthly_budgets (username, month_year, income, spending_added_date) VALUES (?, ?, ?, ?)', (username, month_year, income, date.today()))
    conn.commit()
    conn.close()

# Adds the user's debts to the debts table
def add_debts(debts):
    username = session["username"]
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    for debt in debts:
        cursor.execute(f'INSERT INTO debts (username, debt_name, debt_amount, interest_rate) VALUES (?, ?, ?, ?)', (session['username'], debt[0], debt[1], debt[2]))
    conn.commit()
    conn.close()

# Adds the user's spending for each category in the spending_categories table
def add_spending(spending_categories, month_year):
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute(f'SELECT budget_id FROM monthly_budgets WHERE username = "{session["username"]}" AND month_year = "{month_year}"')
    budget_id = cursor.fetchall()
    for spending_category in spending_categories:
        cursor.execute(f'INSERT INTO spending (budget_id, category, amount) VALUES (?, ?, ?)', (budget_id[0][0], spending_category[0], spending_category[1]))
    conn.commit()
    conn.close()

# Adds the user's goals to the goals table
def add_goals(goals):
    username = session['username']
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    for goal in goals:
        cursor.execute(f'INSERT INTO goals (username, deadline, goal_name, goal_amount) VALUES (?, ?, ?, ?)', (username, goal[2], goal[0], goal[1]))
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

# Retrieves the user's income for a specific month
def retrieve_income(month_year):
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute(f'SELECT income FROM monthly_budgets WHERE username = "{session["username"]}" AND month_year = "{month_year}"')
    income = cursor.fetchall()
    conn.commit()
    conn.close()

    return income

# Calculates the total spending for a specific month
def calculate_total_spending(month_year):
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute(f'SELECT budget_id FROM monthly_budgets WHERE username = "{session["username"]}" AND month_year = "{month_year}"')
    budget_id = cursor.fetchall()
    if budget_id:
        budget_id = budget_id[0][0]
    cursor.execute(f'SELECT amount FROM spending WHERE budget_id = "{budget_id}"')
    all_spending = cursor.fetchall()
    conn.commit()
    conn.close()
    # As the returned array contains tuples with commas, we have to select the value from each tuple
    total_spending = sum(spending[0] for spending in all_spending)
    return total_spending

@app.route('/registration')
@app.route('/registration.html')
def registration():
    return render_template('registration.html')

@app.route('/login')
@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/')
@app.route('/index.html')
def index_page():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

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

@app.route('/get_net_balance_reading', methods=['GET', 'POST'])
def get_net_balance_reading():
    if request.method == 'POST':
        month_year = str(date.today())[:-3]

        income = retrieve_income(month_year)
        if income:
            income = income[0][0]
        else:
            income = 0

        total_spending = calculate_total_spending(month_year)

        net_balance = income - total_spending
        
        return [net_balance]

@app.route('/process_forms', methods=['GET', 'POST'])
def process_forms_route():
    if request.method == 'POST':
        data = request.get_json()
        budget_data = data['JSON_budget_data']
        income_data = data['JSON_income_data']
        goals_data = data['JSON_goals_data']
        debt_data = data['JSON_debt_data']

        month_year = str(date.today())[:-3]

        add_monthly_budget(income_data, month_year)
        add_debts(debt_data)
        add_spending(budget_data, month_year)
        add_goals(goals_data)
        return '[]'

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