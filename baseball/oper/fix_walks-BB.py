# fix Walks to be BB in the database
from . import db_setup as dbs


def fix_walks():

    # run the update
    conn = dbs.engine.connect()
    query = 'UPDATE raw_player_stats SET stat_type=? WHERE stat_type=?'
    conn.execute(query, 'W', 'BB')

    # check your work
    query = 'SELECT COUNT(*) FROM raw_player_stats WHERE stat_type=?'
    results1 = conn.execute(query, 'W').fetchall()
    results2 = conn.execute(query, 'BB').fetchall()
    print(results1, results2)

    conn.close()

    return True


# need to re-generate all stats + pyts tables and remove stat_processor entries from process_log
def batting_table_deletes():

    # run delete data -- NOT DROP
    conn = dbs.engine.connect()
    query = 'DELETE FROM batting'
    query2 = 'DELETE FROM batting_calc'
    conn.execute(query)
    conn.execute(query2)
    query = 'DELETE FROM pitching'
    query2 = 'DELETE FROM fielding'
    conn.execute(query)
    conn.execute(query2)
    query = 'DELETE FROM player_year_team'
    conn.execute(query)

    # remove all stat_processor lines in process_logs
    query = 'DELETE FROM process_log WHERE process_name LIKE ?'
    conn.execute(query, 'stat_processor%')

    # check your work
    query = 'SELECT COUNT(*) FROM batting'
    results = conn.execute(query).fetchall()
    print(results)
    query = 'SELECT COUNT(*) FROM process_log WHERE process_name LIKE ?'
    results = conn.execute(query, 'stat_processor%').fetchall()
    print(results)

    conn.close()

    return True


# fix_walks()
# batting_table_deletes()
# THEN RUN THE runjob generateStats
