# Import flask and template operators
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

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


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/db/')
def db_browser():
    tables = execute_query('SELECT name FROM sqlite_master WHERE type="table"')
    tables.remove(('sqlite_sequence',))
    return render_template('db_browser.html', tables=tables)

@app.route('/db/<table>/')
def table_browser(table):
    
    columns = execute_query('PRAGMA table_info({})'.format(table))
    rows = execute_query('SELECT * FROM {}'.format(table))
    
    return render_template('table_browser.html', table=table, columns=columns, rows=rows)

@app.route('/db/<table>/delete', methods=['GET', 'POST'])
def delete_table(table):
    if request.method == 'POST':
        execute_query('DROP TABLE {}'.format(table))
        flash('Table {} deleted successfully!'.format(table))
        return redirect(url_for('db_browser'))
    return render_template('delete_table.html', table=table)

@app.route('/db/add', methods=['GET', 'POST'])
def add_table():
    if request.method == 'GET':
        return render_template('add_table.html')
    else:
        table = request.form.get('table')
        columns = request.form.getlist('column[]')
        columns = [column.replace(' ', '_') for column in columns]        
        if not table or not columns:
            return "Please fill all of the fields"
        query = """CREATE TABLE {} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {}
            )
        """.format(table, ' TEXT, '.join(columns))
        try:
            execute_query(query)
            return('Table {} created successfully!'.format(table))
        except Exception as e:
            return(str(e))
        

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
        values = request.form.getlist('column[]')
        # add "" for each value in values
        values = ['"{}"'.format(x) for x in values]
        # add column names to values: column1="value1", column2="value2"
        values = [x + '=' + y for x, y in zip(columns.split(', '), values)]
        # make values a string
        values = ', '.join(values)
        
        query = 'UPDATE {} SET {} WHERE id={}'.format(table, values, row_id)
        

        execute_query(query)
        flash('Row updated in {}'.format(table))
        return redirect(url_for('table_browser', table=table))
    columns = execute_query('PRAGMA table_info({})'.format(table))
    data = execute_query('SELECT * FROM {} WHERE id={}'.format(table, row_id))
    columns = columns[1:]
    return render_template('edit_row.html', table=table, row_id=row_id, columns=columns, data=data[0])

@app.route('/db/<table>/search/<column>', methods=['POST'])
def search_table(table, column):
    if request.method == 'POST':
        query = 'SELECT * FROM {} WHERE {} LIKE "%{}%"'.format(table, column, request.form['search'])
        rows = execute_query(query)
        return render_template('table_browser.html', table=table, rows=rows)