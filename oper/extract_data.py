# extracting the data

# libraries
import pandas as pd
import re
import os
import sys
import time as t
from . import game_converter as g
from . import play_processor as pp
from . import stat_collector as sc
from . import global_variables as gv
from . import date_time as dt
import csv

# get argument
year_range = sys.argv[1]

# set a default year
a_year = 2018

# check if range or single
if re.search(r'^(19[0-9]{2}|20[0-9]{2})-(19{2}|20[0-9]{2})$', year_range):
    # add range later
    pass
elif re.search(r'^[0-9]{4}$', year_range):
    a_year = year_range
else:
    # error handling
    pass

# open and read data files
dir_str = 'baseball/import/' + a_year
# for event_file in os.listdir(dir_str):
# print(x)
# file_dir = dir_str + '/' + event_file
all_files = os.listdir(dir_str)

# overwrite STARTERS.csv
fs = open('STARTERS.csv', "w")
fs.close()

# overwrite GAMEPLAY.LOG
fgp = open('GAMEPLAY.LOG', mode="w")
fgp.close()

# total time for 1 year of files
y_time = t.time()

for file_nm in all_files:
    # start timer
    s_time = t.time()

    # get current file
    file_dir = dir_str + '/' + file_nm
    f = open(file_dir, "r")
    f1 = f.readlines()

    # get team name and year
    data_year = a_year
    team_name = file_nm[4:7]

    # collect id and group the games
    games = []
    game_ids = []
    game_info = []
    game_play = []
    game_start = []
    for line_item in f1:
        # Do this check first: if end of file OR (line item is ID and game_play > 0)
        if (line_item.index == f1[-1].index) | ((line_item[:2] == "id") & (len(game_play) > 0)):
            # populate game info, starts, plays
            game_info.append(game_start.copy())
            game_info.append(game_play.copy())
            games.append(game_info.copy())
            game_info.clear()
            game_start.clear()
            game_play.clear()  # Needed to clear this so it doesn't tack on for all remaining games!

        # separate this game with the next
        if line_item[:2] == "id":
            # append game id
            game_ids.append(line_item)
            game_info.append(line_item)
        elif line_item[:4] == "play" or line_item[:3] == "sub":
            game_play.append(line_item)
        elif line_item[:5] == "start":
            game_start.append(line_item)
        else:
            game_info.append(line_item)

    # close the read file
    f.close()
    f1 = None

    # extract all starting lineups by game (replaced each iteration in the variable)
    gv.game_roster = sc.game_tracker(games, data_year)
    games_roster = pd.DataFrame(gv.game_roster).transpose()
    games_roster.to_csv('STARTERS.csv', sep=',', mode='a', index=False)

    # convert all games for 1 file
    a_full_df = g.convert_games(games, games_roster)

    # play_processor2 function
    for e, each_game in enumerate(a_full_df):

        # game performance
        a1_time = t.time()

        # then run the processor
        this_game = pp.play_processor4(each_game, games_roster, team_name, data_year)

        # game performance
        a2_time = t.time()

        # reindex the DICTIONARY keys
        this_game = dict((int(k)+gv.fo_idx, value) for (k, value) in this_game.items())
        gv.fo_idx += len(this_game)

        # game performance
        a3_time = t.time()

        # store into full_output
        gv.full_output.update(this_game)

        # game performance
        a4_time = t.time()
        fgp = open('GAMEPLAY.LOG', mode='a')
        fgp.write('GAME #:' + str(e) + ' process: ' + str(dt.seconds_convert(a2_time - a1_time)) + '\n')
        fgp.write('GAME #:' + str(e) + ' reindex: ' + str(dt.seconds_convert(a3_time - a2_time)) + '\n')
        fgp.write('GAME #:' + str(e) + ' store: ' + str(dt.seconds_convert(a4_time - a3_time)) + '\n')
        fgp.write('GAME #:' + str(e) + ' TOTAL: ' + str(dt.seconds_convert(a4_time - a1_time)) + '\n')
        # print('GAME #:', e, ' TOTAL: ', a4_time - a1_time)
        fgp.close()

    # testing play_processor3
    # pd.DataFrame(gv.full_output).transpose().to_csv('OUTPUT.csv', sep=',', mode='a', index=False)
    # exit()

    # indicator of what is completed
    e_time = t.time()
    print('COMPLETED: ', file_nm, ' - ', dt.seconds_convert(e_time - s_time))
    fgp = open('GAMEPLAY.LOG', mode='a')
    fgp.write('COMPLETED: ' + file_nm + ' - ' + str(dt.seconds_convert(e_time - s_time)) + '\n')
    fgp.close()

    # ------------- SINGLE-TEAM USE ONLY ------------- #
    # '''
    # Write Output File after converting entire list of dict to data frame
    o1_time = t.time()

    print('Completed', a_year, ':', dt.seconds_convert(o1_time - y_time))

    csv_columns = list(gv.full_output[0].keys())
    csv_file = 'OUTPUT_' + file_nm[0:7] + ' .csv'
    try:
        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for l in gv.full_output:
                writer.writerow(gv.full_output[l])
    except IOError:
        print("I/O error")
        exit()

    # CHECK FIELDING STATS
    # t1_time = t.time()
    # gv.player = pd.read_csv('PRE_STATS.csv')
    gv.player_stats = sc.stat_organizer(gv.player)
    # gv.player_stats['batting'].to_csv('BATTING.csv', sep=',', index=False)
    # gv.player_stats['pitching'].to_csv('PITCHING.csv', sep=',', index=False)
    gv.player_stats['fielding'].to_csv('FIELDING.csv', sep=',', index=False)

    exit()
    # '''
    # ------------------------------------------------ #

# Write Output File after converting entire list of dict to data frame
o1_time = t.time()

print('Completed', a_year, ':', dt.seconds_convert(o1_time - y_time))

csv_columns = list(gv.full_output[0].keys())
csv_file = 'OUTPUT.csv'
try:
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for l in gv.full_output:
            writer.writerow(gv.full_output[l])
except IOError:
    print("I/O error")
    exit()

# WRITING OUTPUT PERFORMANCE
o2_time = t.time()
fgp = open('GAMEPLAY.LOG', mode='a')
fgp.write('Processing Games Output File: ' + str(dt.seconds_convert(o2_time - o1_time)) + '\n')
print('Processing Games Output File: ', dt.seconds_convert(o2_time - o1_time))
fgp.close()

# player stats
t1_time = t.time()
# gv.player = pd.read_csv('PRE_STATS.csv')
gv.player_stats = sc.stat_organizer(gv.player)
gv.player_stats['batting'].to_csv('BATTING.csv', sep=',', index=False)
gv.player_stats['pitching'].to_csv('PITCHING.csv', sep=',', index=False)

# WRITING STATS PERFORMANCE
t2_time = t.time()
fgp = open('GAMEPLAY.LOG', mode='a')
fgp.write('Stats Processing: ' + str(dt.seconds_convert(t2_time - t1_time)) + '\n')
print('Stats Processing: ', dt.seconds_convert(t2_time - t1_time))
fgp.close()

# release variables?
gv.full_output = {}
gv.player = {}
gv.player_stats = pd.DataFrame()
