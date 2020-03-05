# this is a testing script to read databases for specific entries
import sqlite3 as sql

conn = sql.connect('baseball.db')
c = conn.cursor()

# select query
# c.execute('''SELECT * FROM starters''')
# c.execute('''SELECT COUNT(*) FROM starters''')

# fetch results
results = c.fetchall()
print(results)
