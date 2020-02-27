# setting up the sqlite database
import sqlite3 as sql

conn = sql.connect('baseball.db')
c = conn.cursor()

# setup database and tables
c.execute('''CREATE TABLE starters
            (game_id text, player_id text, player_nm text, team_id int, 
            team_name text, bat_lineup int, fielding int)''')
conn.commit()
