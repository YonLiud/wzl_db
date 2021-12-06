# Import flask and template operators
from flask import Flask, render_template
import sqlite3

# Define WSGI object
app = Flask(__name__)

# Configurations
app.config.from_object('config')



def execute_query(query):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query)
    callback = cursor.fetchall()
    cursor.close()
    conn.close()
    return callback

# HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# Home page view
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/db/')
def db_browser():
    # Get all the tables
    tables = execute_query('SELECT name FROM sqlite_master WHERE type="table"')
    # remove table called sqlite_sequence from the list
    tables.remove(('sqlite_sequence',))
    return render_template('db_browser.html', tables=tables)

@app.route('/db/<table>/')
def table_browser(table):
    
    columns = execute_query('PRAGMA table_info({})'.format(table))
    rows = execute_query('SELECT * FROM {}'.format(table))
    
    return render_template('table_browser.html', table=table, columns=columns, rows=rows)