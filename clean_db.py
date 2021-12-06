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
cursor.execute("""CREATE TABLE department (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT)""")
conn.commit()
# add data to table department
cursor.execute("""INSERT INTO department (name) VALUES ('HR')""")
cursor.execute("""INSERT INTO department (name) VALUES ('AD')""")
# add data to table employee
cursor.execute("""INSERT INTO emplyee (name, department_id, comments) VALUES ('Xin KeDaiKa', "1", 'Bad')""")
cursor.execute("""INSERT INTO emplyee (name, department_id, comments) VALUES ('Emma Sinclair', "2", 'Great')""")
cursor.execute("""INSERT INTO emplyee (name, department_id, comments) VALUES ('Solomon Gold', "1", 'Great')""")

conn.commit()