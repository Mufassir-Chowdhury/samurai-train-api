import os
import sqlite3

db = sqlite3.connect(os.environ.get('DATABASE_NAME'))

cursor = db.cursor()

cursor.execute('DROP TABLE IF EXISTS users')
cursor.execute('DROP TABLE IF EXISTS stations')
cursor.execute('DROP TABLE IF EXISTS trains')
cursor.execute('DROP TABLE IF EXISTS train_stops')

db.commit()
