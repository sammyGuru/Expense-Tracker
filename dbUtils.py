import sqlite3
import pandas as pd
import datetime as dt

DATABASE_NAME = "expenses.db"

DEFAULT_CATEGORIES = ["Rent","Utilities","Groceries"]

cat_list = ""
for i in DEFAULT_CATEGORIES:
    cat_list = cat_list+"(\"" + i + "\"), " # constructs a string cat_list that represents SQL values for inserting categories.
#("Rent"), ("Utilities"), ("Groceries"),

def create_tables():
    connection = sqlite3.connect(DATABASE_NAME)
    #establishes a connection to the expenses.db database using sqlite3.connect(). If the database does not exist, SQLite creates it.
    cursor = connection.cursor()
    # cursor acts as a conduit between the Python program and the database, handling SQL execution and data retrieval.

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS category(
                   id INTEGER PRIMARY KEY,
                   category TEXT
                   )
                   ''')
    
    cat_query = 'SELECT category from category'
    category_list = pd.read_sql_query(cat_query,connection).category.to_list() #runs the SQL query and converts the result into a pandas DataFrame,category column is extracted and converted to a list
    if len(category_list) == 0:
        cursor.executemany('INSERT INTO category (category) VALUES (?)', [(cat,) for cat in DEFAULT_CATEGORIES])
        #INSERT INTO category (category) VALUES ("Rent"), ("Utilities"), ("Groceries"): by removing the trailing comma

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS expenses(
                   id INTEGER PRIMARY KEY,
                   date INTEGER,
                   category_id INTEGER,
                   amount REAL,
                   FOREIGN KEY (category_id) REFERENCES category(id)
                   )
                   ''')
    # A foreign key reference to the id column in the category table, establishing a relationship between expenses and categories.
    connection.commit()
    connection.close()

def get_category_list():
    connection = sqlite3.connect(DATABASE_NAME)
    query = '''
    SELECT c.id, c.category
    FROM category c
    '''
    df = pd.read_sql_query(query,connection)
    connection.close()
    return df.category.to_list()

def save_category(new_choice):
    new_choice = new_choice.title()
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cat_query = 'SELECT category FROM category'
    category_list = pd.read_sql_query(cat_query,connection).category.to_list()

    if new_choice in category_list:
        result = new_choice+" already exists in the list of categories"
    else:
        cursor.execute('INSERT INTO category (category) VALUES (?)', (new_choice,))
        result = new_choice + " added successfully to the list of categories"

    connection.commit()
    connection.close()

def save_expense(date,category,amount):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute('SELECT id from category WHERE category = ?', (category,))
    row = cursor.fetchone()
    cat_id = row[0]

    try:
        cursor.execute('INSERT INTO expenses(date,category_id,amount) VALUES (?,?,?)', (date,cat_id,amount))
        result = "Expense record saved successfully"
    except:
        result = "Oops something isnt right. Check your inputs again"
    
    connection.commit()
    connection.close()

    return result

def get_expenses():
    connection = sqlite3.connect(DATABASE_NAME)
    query = '''
    SELECT e.date,c.category,e.amount
    FROM expenses e
    LEFT JOIN category c ON c.id = e.category_id
    '''
    df = pd.read_sql_query(query,connection)
    connection.close()
    return df