"""
import sqlite3

conn = sqlite3.connect('data/users.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM users LIMIT 5")
print(cursor.fetchall())
conn.close()
""" 