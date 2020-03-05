# this is a testing script to read databases for specific entries
import sqlite3 as sql

conn = sql.connect('baseball.db')
c = conn.cursor()

# select query
# c.execute('''SELECT * FROM starters''')
# c.execute('''SELECT COUNT(*) FROM starters''')

# check if table exists
try:
    table_nm = 'starters'
    value = '1'
    sql_query = '''SELECT * FROM ''' + table_nm + ''' WHERE fielding = ?'''
    print(sql_query)
    c.execute(sql_query, value)
except sql.Error as e:
    print('ERROR')
    print(e)
    exit()

# fetch results
results = c.fetchall()
print(results)
