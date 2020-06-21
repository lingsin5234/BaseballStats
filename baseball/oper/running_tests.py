# this file is to run tests of the oper files ONLY
from . import import_retrosheet as ir
from . import process_imports as pi
from . import generate_statistics as gs
from . import aggregate_statistics as ag
from . import database_reader as dr
from . import fix_quotes_in_names as fqn
from . import db_setup as dbs
from . import date_time as dt
from . import automated_tests as aut
from . import calculate_statistics as cs
from . import extract_teams_players as etp
import time as t
import os
import re
import pandas as pd

# '''
# run from scratch
for yr in reversed(range(2017, 2020)):
    # import Year; print True if completed
    print("Import Completed: ", ir.import_data(yr))

    # run the extract_player/teams
    etp.extract_teams(yr)
    etp.extract_players(yr)

    start_time = t.time()
    files = os.listdir('baseball/import/' + str(yr))
    files = [f[4:7] for f in files if f.find('ROS') == -1 and f.find('TEAM') == -1]
    for f in files:
        print("Processing Completed: ", f, pi.process_data_single_team(yr, f))
    print("Stats Generated: ", 'Batting', gs.generate_stats2(yr, 'batting'))
    print("Stats Generated: ", 'Pitching', gs.generate_stats2(yr, 'pitching'))
    print("Stats Generated: ", 'Fielding', gs.generate_stats2(yr, 'fielding'))
    # print("All Processing Completed", dt.seconds_convert(t.time() - start_time))

    aut.import_test_cases(yr)
    print('Test Cases IMPORTED.')
    aut.run_test_cases('batting', yr)
    print('Test Cases for batting completed.')
    aut.run_test_cases('fielding', yr)
    print('Test Cases for fielding completed.')

    # '''
    conn = dbs.engine.connect()
    query = 'SELECT * FROM batting WHERE data_year=?'
    results = conn.execute(query, yr).fetchall()
    columns = conn.execute(query, yr)
    conn.close()
    # '''

    # --- run calc bat stats --- #
    cs.calculate_bat_stats(results, columns, yr)

    '''
    # select to see results
    conn = dbs.engine.connect()
    query = 'SELECT * FROM batting_calc'
    results = conn.execute(query).fetchall()
    columns = conn.execute(query)
    df = pd.DataFrame(results)
    df.columns = columns.keys()
    print(df)
    conn.close()
    '''
# '''
'''
# ^ above done wrong. should be processing ALL stats before doing a generate stats!
query = "SELECT COUNT(*) FROM pitching"
results = dr.baseball_db_reader(query)
print(results)
'''
# print True if aggregate_statistics is completed
# print("Statistics Aggregated: ", ag.stats_aggregate(2018))

'''
# test run for removing strings
fqn.remove_quotes_fix()
'''
'''
# Check the gameplay table
query = "SELECT * FROM gameplay LIMIT 10"
results = dr.baseball_db_reader(query)
print(results)

# Check the processing_errors table
query = "SELECT * FROM processing_errors"
results = dr.baseball_db_reader(query)
print(results)

# Show all tables
print(dbs.engine.table_names())
'''

#  -----  Fielder's Choice Fix  -----  #
'''
# load the imports for 2018 then find FC
FC = []
dir_str = 'baseball/import/2018'
all_files = os.listdir(dir_str)

for file_nm in all_files:
    # get current file
    file_dir = dir_str + '/' + file_nm
    f = open(file_dir, "r")
    f1 = f.readlines()

    for line_item in f1:
        if line_item[0:4] == 'play':
            play = line_item.split(',')
            play = play[len(play)-1].replace('\n', '')
            if bool(re.search(r'X[123H]\(', play)):
                FC.append(play)

FC = list(set(FC))
for f in FC:
    print(f)
'''
#  ----------------------------------  #

'''
# Using Albert Pujols as a check, load PRE_STATS and sort for pujoa001
# Second check, Trea turner; turnt001
df = pd.read_csv('PRE_STATS.csv')
df = df[(df['player_id'] == 'pujoa001') & (df['bat_pitch'] == 'fielding')]
pujols = df.groupby(['game_id', 'stat_type']).agg({'stat_value': 'sum'}).reset_index()
pujols = pujols.set_index(['game_id']).pivot(columns='stat_type')['stat_value'].reset_index()
pujols['game_id'] = pujols['game_id'].apply(lambda x: re.sub(r'^[A-Z]{3}', '', x))
pujols = pujols.sort_values('game_id')
pujols.to_csv('pujols.csv', index=False)
# df.to_csv('turntrea.csv', index=False)
'''
