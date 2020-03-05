# setting up the sqlite database using sqlalchemy
import sqlite3 as sql
import sqlalchemy as sa

# constants
starter_col = 'game_id text, player_id text, player_nm text, team_id int, team_name text, bat_lineup int, fielding int'
gameplay_col = 'game_id text, type text, inning int, half int, half_innings text, playerID text, count text, ' \
               'pitches text, play text, player_name text, team_id text, team_name text, batting int, fielding int, ' \
               'pitcherID text, outs int, 1B_before text, 2B_before text, 3B_before text, 1B_after text, ' \
               '2B_after text, 3B_after text, runs_scored int, total_scored int'


# setup engine and database
engine = sa.create_engine('sqlite:///baseball.db', echo=True)
