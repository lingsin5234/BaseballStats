# setting up the sqlite database
import sqlite3 as sql

# constants
starter_col = 'game_id text, player_id text, player_nm text, team_id int, team_name text, bat_lineup int, fielding int'
gameplay_col = 'game_id text, type text, inning int, half int, half_innings text, playerID text, count text, ' \
               'pitches text, play text, player_name text, team_id text, team_name text, batting int, fielding int, ' \
               'pitcherID text, outs int, 1B_before text, 2B_before text, 3B_before text, 1B_after text, ' \
               '2B_after text, 3B_after text, runs_scored int, total_scored int'


# setup database and tables
def create_tables(table_nm, col_nm):

    conn = sql.connect('baseball.db')
    c = conn.cursor()

    # first check if exists before creating
    try:
        c.execute('''SELECT * FROM ''' + table_nm)
    except sql.Error:
        try:
            sql_query = '''CREATE TABLE ''' + table_nm + ''' (?)'''
            print(sql_query)
            c.execute(sql_query, col_nm)
        except sql.Error as e:
            print("Error on SELECT and CREATE TABLE for '", table_nm, "'.")
            print(e)
            exit()
        conn.commit()
    c.close()


# create tables for starters, gameplay
create_tables('starters', starter_col)
create_tables('gameplay', gameplay_col)
