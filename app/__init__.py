# Import flask and template operators
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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
    conn.commit()
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

@app.route('/db/add', methods=['GET', 'POST'])
def add_table():
    if request.method == 'GET':
        return render_template('add_table.html')
    else:
        table = request.form.get('table')
        skills = request.form.getlist('column[]')
        query = """CREATE TABLE {} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {}
            )
        """.format(table, ' TEXT, '.join(skills))
        execute_query(query)
        return redirect(url_for('db_browser'))

@app.route('/db/<table>/add', methods=['GET', 'POST'])
def add_row(table):
    if request.method == 'POST':
        columns = execute_query('PRAGMA table_info({})'.format(table))
        columns = [x[1] for x in columns]
        columns.remove('id')
        columns = ', '.join(columns)
        values = [request.form[x] for x in request.form]
        values = ['"{}"'.format(x) for x in values]
        values = ', '.join(values)
        query = 'INSERT INTO {} ({}) VALUES ({})'.format(table, columns, values)
        execute_query(query)
        flash('Row added to {}'.format(table))
        return redirect(url_for('table_browser', table=table))
    columns = execute_query('PRAGMA table_info({})'.format(table))
    return render_template('add_row.html', table=table, columns=columns)

@app.route('/db/<table>/<row_id>/delete', methods=['GET', 'POST'])
def delete_row(table, row_id):
    if request.method == 'POST':
        query = 'DELETE FROM {} WHERE id={}'.format(table, row_id)
        execute_query(query)
        flash('Row deleted from {}'.format(table))
        return redirect(url_for('table_browser', table=table))
    row = execute_query('SELECT * FROM {} WHERE id={}'.format(table, row_id))
    columns = execute_query('PRAGMA table_info({})'.format(table))
    return render_template('delete_row.html', table=table, rows=row[0], columns=columns)

@app.route('/db/<table>/<row_id>/edit', methods=['GET', 'POST'])
def edit_row(table, row_id):
    if request.method == 'POST':
        columns = execute_query('PRAGMA table_info({})'.format(table))
        columns = [x[1] for x in columns]
        columns.remove('id')
        columns = ', '.join(columns)
        values = [request.form[x] for x in request.form]
        values = ['"{}"'.format(x) for x in values]
        values = ', '.join(values)
        query = 'UPDATE {} SET {} WHERE id={}'.format(table, values, row_id)
        execute_query(query)
        flash('Row updated in {}'.format(table))
        return redirect(url_for('table_browser', table=table))
    columns = execute_query('PRAGMA table_info({})'.format(table))
    return render_template('edit_row.html', table=table, row_id=row_id, columns=columns)