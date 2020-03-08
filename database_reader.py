# this is a testing script to read databases for specific entries
import sqlite3 as sql
import sqlalchemy as sa
import db_setup as dbs

# query
c = dbs.engine.connect()
# results1 = c.execute("SELECT * FROM starters WHERE game_id LIKE 'BOS%' LIMIT 5").fetchall()
# results2 = c.execute("SELECT * FROM gameplay WHERE game_id LIKE 'BOS%' LIMIT 5").fetchall()
# print('STARTERS', results1)
# print('GAMEPLAY', results2)
# results = c.execute("SELECT * FROM pitching WHERE team_name = 'TOR'").fetchall()
# results = c.execute("SELECT * FROM raw_player_stats WHERE player_id = 'axfoj001' and stat_type = 'BT'").fetchall()
# results = c.execute("SELECT * FROM pitching WHERE player_id = 'axfoj001'").fetchall()
results = c.execute("SELECT * FROM process_log").fetchall()
print(results)
# c.execute('DROP TABLE starters')

# conn = sql.connect('baseball.db')
# c = conn.cursor()
#
# # select query
# # c.execute('''SELECT * FROM starters''')
# # c.execute('''SELECT COUNT(*) FROM starters''')
#
# # check if table exists
# try:
#     table_nm = 'starters'
#     value = '1'
#     sql_query = '''SELECT * FROM ''' + table_nm + ''' WHERE fielding = ?'''
#     print(sql_query)
#     c.execute(sql_query, value)
# except sql.Error as e:
#     print('ERROR')
#     print(e)
#     exit()
#
# # fetch results
# results = c.fetchall()
# print(results)
