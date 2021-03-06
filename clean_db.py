from sqlite3.dbapi2 import Cursor
import sys, os, sqlite3

# remove database.db file
if os.path.exists('database.db'):
    os.remove('database.db')
    
# create database.db file
conn = sqlite3.connect('database.db')

# create cursor
cursor = conn.cursor()

# create tables

cursor.execute("""CREATE TABLE emplyee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    department_id TEXT,
    comments TEXT)""")
conn.commit()