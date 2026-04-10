# Necessary libraries and packages are imported
from flask import Flask, render_template, request, redirect, url_for, session, Response
import sqlite3
import json
from datetime import date
import matplotlib
# This renders plots to images rather than displaying them
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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

# Retrieves the user's spending for a specific month
def get_user_spending(month_year):
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute(f'SELECT budget_id FROM monthly_budgets WHERE month_year = "{month_year}" AND username = "{session["username"]}"')
    budget_id = cursor.fetchall()
    if not budget_id:
        return False
    cursor.execute(f'SELECT category, amount FROM spending WHERE budget_id = {budget_id[0][0]}')
    categories = cursor.fetchall()

    conn.commit()
    conn.close()

    return categories

# Calculates the difference in amount spent on each category between a target month and the month before it
def get_user_spending_differences(month_year, previous_month_year):
    current_spending = get_user_spending(month_year)
    previous_spending = get_user_spending(previous_month_year)
    
    # For a difference in spending to be calculated, there has to be a spending form for the target month or previous month
    if not current_spending or not previous_spending:
        return False

    # There is no guarantee that the categories in each month are in the same order, as users may add their custom categories in different orders each time
    # To get around this, the spending for each month is converted to a dictionary to access the amount for each category through key-value pairs
    current_spending = {category:amount for category, amount in current_spending}
    previous_spending = {category:amount for category, amount in previous_spending}

    current_categories = []
    spending_differences = []

    for category in current_spending:
        if previous_spending.get(category):
            difference = current_spending[category] - previous_spending[category]
            spending_differences.append(difference)
            current_categories.append(category)
    
    return [current_categories, spending_differences]

# Retrieves the user's spending history
def get_all_user_spending():
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    # Retrieves all the budget ids associated with the user
    cursor.execute(f'SELECT budget_id FROM monthly_budgets WHERE username = "{session["username"]}"')
    budget_ids = cursor.fetchall()
    all_user_spending = []
    for budget_id in budget_ids:
        cursor.execute(f'SELECT category, amount FROM spending WHERE budget_id = {budget_id[0]}')
        categories_and_amount = cursor.fetchall()
        all_user_spending.append(categories_and_amount)
    
    return all_user_spending

# Retrieves all of the user's goals
def get_all_goals():
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute(f'SELECT goal_name, goal_amount, deadline FROM goals WHERE username = "{session["username"]}"')
    goals = cursor.fetchall()
    
    return goals

# Generates a forecasted spending for each of the user's spending categories
def calculate_spending_forecast():
    all_user_spending = get_all_user_spending()
    all_spending_dict = []
    for spending in all_user_spending:
        # Turns each month's spending into a dictionary
        # This is to easily retrieve a category's spending regardless of its order in its respective spending list
        all_spending_dict.append({category:amount for category, amount in spending})

    # Keeps a list of all spending categories that the user ever had
    categories = []

    for spending in all_spending_dict:
        categories += (list(spending.keys()))

    categories = list(set(categories)) # Removes all duplicate categories
    # This is to keep track of all spending on a category
    category_history = {category:[] for category in categories}
    forecasted_spending = {category:0 for category in categories}

    for category in categories:
        for spending in all_spending_dict:
            # Adds a category's spending to its history
            category_history[category].append(spending.get(category, 0))
    
    # Applies a weighted moving average to each category
    for category in category_history:
        average = 0
        for i in range(len(category_history[category])):
            average += round((i+1)/len(category_history[category]) * category_history[category][i], 2)
        forecasted_spending[category] = average

    return forecasted_spending

# Calculates the target for each of the user's goals
def calculate_goals_targets():
    all_goals = get_all_goals()
    goals_targets = {}

    for goal in all_goals:
        current_date = date.today()
        goal_deadline = goal[2]
        days_left = (date(int(goal_deadline[:4]), int(goal_deadline[5:7]), int(goal_deadline[8:10])) - current_date).days
        if days_left >  0:
            # As the number of days left decreases, the urgency approaches 1
            urgency = 1/days_left
        else:
            # If today is the deadline or the deadline has passed, then the highest urgency is assigned
            # So, the user would have to pay it fully if they want to meet their goal
            urgency = 1

        target = urgency * goal[1]

        goals_targets.update({goal[0]: target})
            
    return goals_targets

# Adds the savings goal to forecasted_goals
def add_savings(savings, forecast_id):
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO forecast_goals (forecast_id, goal_name, goal_amount) VALUES (?, ?, ?)', (forecast_id, 'savings', savings))
    conn.commit()
    conn.close()

# Calculates a maximum spending target and savings in the forecast page
def calculate_maximum_spending_target_and_savings(forecasted_budget, goals_targets):
    total_forecasted_spending = sum(list(forecasted_budget.values())) + sum(list(goals_targets.values()))

    # Aiming to spend 10% less than you expect to is a healthy budgeting goal 
    maximum_spending_target = 0.9 * total_forecasted_spending
    # Aiming to save (atleast) 10% of your spending is a good savings goal
    savings = 0.1 * total_forecasted_spending

    return [maximum_spending_target, savings]

# Retrieves the forecast id associated with a specific month's spending
def get_forecast_id(month_year):
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute(f'SELECT budget_id FROM monthly_budgets WHERE username = "{session["username"]}" AND month_year = "{month_year}"')
    budget_id = cursor.fetchall()
    if budget_id:
        budget_id = budget_id[0][0]

        cursor.execute(f'SELECT forecast_id FROM forecasts WHERE budget_id = "{budget_id}"')
        fetched_data = cursor.fetchall()
        if fetched_data:
            forecast_id = fetched_data[0][0]
            return forecast_id
    else:
        return ''
    conn.commit()
    conn.close()

# Retrieves the user's maximum spending target
def get_maximum_spending_target(forecast_id):
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute(f'SELECT spending_cap FROM forecasts WHERE forecast_id = "{forecast_id}"')
    spending_cap = cursor.fetchall()[0][0]

    conn.commit()
    conn.close()

    return spending_cap

# Retrieves the user's goal targets
def get_goals_targets(forecast_id):
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute(f'SELECT goal_name, goal_amount FROM forecast_goals WHERE forecast_id = "{forecast_id}"')
    goals_targets = cursor.fetchall()[0][0]

    goals_targets = {goal_name:goal_amount for goal_name, goal_amount in goals_targets}

    conn.commit()
    conn.close()

    return goals_targets

# Retrieves the user's forecasted budget
def get_forecasted_budget(forecast_id):
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute(f'SELECT category_name, forecast_amount FROM forecast_categories WHERE forecast_id = "{forecast_id}"')
    forecasted_budget = cursor.fetchall()[0][0]

    forecasted_budget = {category_name:forecast_amount for category_name, forecast_amount in forecasted_budget}

    conn.commit()
    conn.close()

    return forecasted_budget

# Retrieves the user's savings target
def get_savings(forecast_id):
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute(f'SELECT goal_amount FROM forecast_goals WHERE forecast_id = "{forecast_id}" AND goal_name = "savings"')
    savings = cursor.fetchall()

    conn.commit()
    conn.close()

    return savings

# Adds a forecast to forecasts
def add_forecast(month_year, maximum_spending_taget):
    date_today = date.today()

    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()
    cursor.execute(f'SELECT budget_id FROM monthly_budgets WHERE username = "{session["username"]}" AND month_year = "{month_year}"')
    budget_id = cursor.fetchall()
    if budget_id:
        budget_id = budget_id[0][0]
        cursor.execute(f'INSERT INTO forecasts (budget_id, created_date, spending_cap) VALUES (?, ?, ?)', (budget_id, date_today, maximum_spending_taget))
    conn.commit()
    conn.close()

# Adds a forecast goal to forecast_goals
def add_forecast_goals(forecast_id, goals_targets):
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()

    for goal in goals_targets:
        cursor.execute(f'INSERT INTO forecast_goals (forecast_id, goal_name, goal_amount) VALUES (?, ?, ?)', (forecast_id, goal, goals_targets[goal]))

    conn.commit()
    conn.close()

# Adds the forecasted spending for each category to forecast_categories
def add_forecast_categories(forecast_id, forecasted_budget):
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()

    for category in forecasted_budget:
        cursor.execute(f'INSERT INTO forecast_categories (forecast_id, category_name, forecast_amount) VALUES (?, ?, ?)', (forecast_id, category, forecasted_budget[category]))

    conn.commit()
    conn.close()

# Updates the user's maximum spending target
def update_maximum_target(maximum_spending_target, month_year):
    conn = sqlite3.connect(DB_path)
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()

    cursor.execute(f'SELECT budget_id FROM monthly_budgets WHERE username = "{session["username"]}" AND month_year = "{month_year}"')
    budget_id = cursor.fetchall()[0][0]

    cursor.execute(f'UPDATE forecasts SET spending_cap = {maximum_spending_target} WHERE budget_id = {budget_id}')
    conn.commit()
    conn.close()

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

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

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

@app.route('/spending_insights')
@app.route('/spending_insights.html')
def spending_insights_route():
    if 'username' in session:
        return render_template('spending_insights.html')
    return redirect(url_for('login'))

@app.route('/generate_total_spending_plot/<month_year>', methods=['GET', 'POST'])
def generate_total_spending_plot(month_year):
    if request.method == 'POST':
        all_spending = get_user_spending(month_year)

        # If there is no spending to generate a plot for, no plot is generated
        if not all_spending:
            return ['False']

        # Creates two separate lists to act as the axis
        categories = []
        spending = []

        for category in all_spending:
            categories.append(category[0])
            spending.append(category[1])

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.set_title('Total Spending per Category')
        ax.set_xlabel('Category')
        ax.set_ylabel('Amount, £')
        ax.bar(categories, spending, width=0.5)
        
        # Saves the generated plot to memory to be passed to the frontend.
        img = io.BytesIO()
        fig.savefig(img, format="png")
        plt.close(fig)
        img.seek(0)

        return Response(img.getvalue(), mimetype="image/png")

@app.route('/generate_percentage_total_spending_plot/<month_year>', methods=['GET', 'POST'])
def generate_percentage_total_spending_plot(month_year):
    if request.method == 'POST':
        all_spending = get_user_spending(month_year)

        # If there is no spending to generate a plot for, no plot is generated
        if not all_spending:
            return ['False']

        # Creates two separate lists to act as the axis
        categories = []
        spending = []
        sum = 0

        for category in all_spending:
            categories.append(category[0])
            spending.append(category[1])
            sum += category[1]
        if sum == 0:
            # This avoids dividing by 0
            spending = [0 for item in spending]
        else:
            for i in range(len(spending)):
                spending[i] = round(spending[i]/sum*100, 2)

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.set_title('Percentage of Total Spending per Category')
        ax.set_xlabel('Category')
        ax.set_ylabel('Percentage, %')
        ax.bar(categories, spending, width=0.5)
                
        # Saves the generated plot to memory to be passed to the frontend.
        img = io.BytesIO()
        fig.savefig(img, format="png")
        plt.close(fig)
        img.seek(0)

        return Response(img.getvalue(), mimetype="image/png")

@app.route('/generate_spending_change_plot/<month_year>/<previous_month_year>', methods=['GET', 'POST'])
def generate_spending_change_plot(month_year, previous_month_year):
    if request.method == 'POST':
        user_spending_differences = get_user_spending_differences(month_year, previous_month_year)

        if user_spending_differences:
            current_categories = user_spending_differences[0]
            spending_differences = user_spending_differences[1]
        else:
            # If there are no user spending differences, no plot is generated
            return ['False']

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.set_title('Spending Change per Category')
        ax.set_xlabel('Category')
        ax.set_ylabel('Change, £')
        ax.bar(current_categories, spending_differences, width=0.5)
        
        # Saves the generated plot to memory to be passed to the frontend.
        img = io.BytesIO()
        fig.savefig(img, format="png")
        plt.close(fig)
        img.seek(0)

        return Response(img.getvalue(), mimetype="image/png")

@app.route('/retrieve_sum/<month_year>', methods=['GET', 'POST'])
def retrieve_sum(month_year):
    spending = get_user_spending(month_year)

    # If there are no spending for the target month, there is no sum to be returned
    if not spending:
        return ['False']

    sum = 0
    for category in spending:
        sum += category[1]
    
    return [str(sum)]

@app.route('/retrieve_current_and_previous_spending/<month_year>/<previous_month_year>', methods=['GET', 'POST'])
def retrieve_current_and_previous_spending(month_year, previous_month_year):
    if request.method == 'POST':
        user_spending = get_user_spending(month_year)
        user_spending_differences = get_user_spending_differences(month_year, previous_month_year)

        if not user_spending:
            return ['False']
        elif not user_spending_differences:
            return [user_spending, 'False']
        else:
            return [user_spending, user_spending_differences]

@app.route('/spending_forecasts')
@app.route('/spending_forecasts.html')
def spending_forecasts_route():
    if 'username' in session:
        return render_template('spending_forecasts.html')
    return redirect(url_for('login'))

@app.route('/receive_spending_forecast/<month_year>', methods=['GET', 'POST'])
def receive_spending_forecast(month_year):
    if request.method == 'POST':
        conn = sqlite3.connect(DB_path)
        conn.execute('PRAGMA foreign_keys = 1')
        cursor = conn.cursor()
        cursor.execute(f'SELECT spending_added_date FROM monthly_budgets WHERE username = "{session["username"]}" AND month_year = "{month_year}"')
        date_added = cursor.fetchall()
        # Finds the date that the last forecast for the next month was generated

        conn.commit()
        conn.close()

        if date_added:
            date_added = date_added[0][0]
            days_difference = (date(int(date_added[:4]), int(date_added[5:7]), int(date_added[8:10])) - date.today()).days
        # If a forecast was generated after a spending was submitted, no new forecast is generated
        # If a spending was submitted after a forecast was generated, a new forecast is generated
        else:
            days_difference = 0

        if days_difference <= 0:
            # Generates a forecast
            forecasted_budget = calculate_spending_forecast()
            goals_targets = calculate_goals_targets()
            maximum_spending_target_and_savings = calculate_maximum_spending_target_and_savings(forecasted_budget, goals_targets)
            maximum_spending_target = maximum_spending_target_and_savings[0]
            savings = maximum_spending_target_and_savings[1]

            # Stores the forecast in the database
            add_forecast(month_year, maximum_spending_target)
            forecast_id = get_forecast_id(month_year)
            add_forecast_goals(forecast_id, goals_targets)
            add_savings(savings, forecast_id)
            add_forecast_categories(forecast_id, forecasted_budget)

            return [forecasted_budget, goals_targets, maximum_spending_target, savings]
        else:
            # Retrieves a previously generated forecast
            forecast_id = get_forecast_id(month_year)
            forecasted_budget = get_forecasted_budget(forecast_id)
            maximum_spending_target = get_maximum_spending_target(forecast_id)
            goals_targets = get_goals_targets(forecast_id)
            savings = get_savings(forecast_id)

            return [forecasted_budget, goals_targets, maximum_spending_target, savings]

@app.route('/target_feedback/<maximum_spending_target>/<feedback>', methods=['GET', 'POST'])
def target_feedback(maximum_spending_target, feedback):
    if request.method == 'POST':
        month_year = str(date.today())[:-3]
        maximum_spending_target = float(maximum_spending_target[1:])
        # Depending on the user's feedback, the maximum spending target is adjusted
        if feedback == 'hard':
            new_maximum_spending_target = round(maximum_spending_target * 0.95, 2)
        else:
            new_maximum_spending_target = round(maximum_spending_target * 1.05, 2)
        
        update_maximum_target(new_maximum_spending_target, month_year)
        return [new_maximum_spending_target]

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