# this is a testing script to read databases for specific entries
import sqlite3 as sql
import sqlalchemy as sa
from . import db_setup as dbs
import datetime
import pandas as pd

# query
# c = dbs.engine.connect()
# query = 'SELECT data_year, stat_category, COUNT(*) FROM player_year_team GROUP BY data_year, stat_category'
# query = 'SELECT COUNT(DISTINCT pyts_id) FROM batting_calc'
# query = 'SELECT * FROM process_log'
# results = c.execute(query).fetchall()
# print(results)
# columns = c.execute(query)
# df = pd.DataFrame(results)
# df.columns = columns.keys()
# print(df.head())
# print(len(results))
# print(str(datetime.datetime.now()))
# c.execute("DROP TABLE batting_calc")
'''
c.execute("DROP TABLE batting")
c.execute("DROP TABLE pitching")
c.execute("DROP TABLE fielding")
'''
# results1 = c.execute("SELECT * FROM starters WHERE game_id LIKE 'BOS%' LIMIT 5").fetchall()
# results2 = c.execute("SELECT * FROM gameplay WHERE game_id LIKE 'BOS%' LIMIT 5").fetchall()
# print('STARTERS', results1)
# print('GAMEPLAY', results2)
# results = c.execute("SELECT * FROM pitching WHERE team_name = 'TOR'").fetchall()
# results = c.execute("SELECT * FROM raw_player_stats WHERE player_id = 'axfoj001' and stat_type = 'BT'").fetchall()
# results = c.execute("SELECT * FROM pitching WHERE player_id = 'axfoj001'").fetchall()
# results = c.execute("SELECT * FROM process_log").fetchall()
# results = c.execute("SELECT * FROM processing_errors").fetchall()
# print(results)
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


def baseball_db_reader(query):

    engine = sa.create_engine('sqlite:///baseball.db', echo=True)
    # c = dbs.engine.connect()
    c = engine.connect()
    try:
        results = c.execute(query).fetchall()
    except Exception as e:
        print("Something went wrong with the db_reader", e)
        c.close()
        return False

    return results


# add a DELETE FROM option
def baseball_db_remove(query):

    engine = sa.create_engine('sqlite:///baseball.db', echo=True)
    # c = dbs.engine.connect()
    c = engine.connect()
    try:
        c.execute(query)
    except Exception as e:
        print("Something went wrong with the db_remove")
        c.close()
        return False

    return True
