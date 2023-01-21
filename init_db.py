import sqlite3
connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

curr = connection.cursor()

curr.execute(
    "INSERT INTO users (username, password, email) VALUES (?,?,?)",
    ('admin', 'Abcd1234@', 'test@abc.com')
)

connection.commit()
connection.close()