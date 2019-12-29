# extracting the data

# libraries
import pandas as pd
import re
import os
import sys
import time as t
import game_converter as g
import play_processor as pp
import stat_collector as sc
import global_variables as gv


# get argument
year_range = sys.argv[1]

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
dir_str = 'retrodata/' + a_year
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

for file_nm in all_files:
    # start timer
    s_time = t.time()

    # get current file
    file_dir = dir_str + '/' + file_nm
    f = open(file_dir, "r")
    f1 = f.readlines()

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
    gv.game_roster = sc.game_tracker(games, game_ids)
    gv.game_roster.to_csv('STARTERS.csv', sep=',', mode='a', index=False)

    # convert all games for 1 file
    a_full_df = g.convert_games(games)

    # play_processor2 function
    for e, each_game in enumerate(a_full_df):
        # check by game
        a1_time = t.time()

        # add the game_ids first
        current_game_id = game_ids[e].replace('\n', '')
        current_game_id = current_game_id.replace('id,', '')
        each_game.insert(0, 'game_id', current_game_id)

        # game performance
        a2_time = t.time()

        # then run the processor
        this_game = pp.play_processor2(e+1, each_game)

        # game performance
        a3_time = t.time()

        # reindex the columns once
        this_game = this_game.reindex(this_game.columns, axis=1)

        # convert to dict, store into full_output
        this_dict = this_game.to_dict()
        gv.full_output[gv.fo_idx] = this_dict
        gv.fo_idx += 1

        # game performance
        a4_time = t.time()
        fgp = open('GAMEPLAY.LOG', mode='a')
        fgp.write('GAME #:' + str(e) + ' prep: ' + str(a2_time - a1_time) + '\n')
        fgp.write('GAME #:' + str(e) + ' process: ' + str(a3_time - a2_time) + '\n')
        fgp.write('GAME #:' + str(e) + ' reindex: ' + str(a4_time - a3_time) + '\n')
        fgp.write('GAME #:' + str(e) + ' TOTAL: ' + str(a4_time - a1_time) + '\n')
        # print('GAME #:', str(e), ' TOTAL: ', str(a4_time - a1_time))
        fgp.close()

    # indicator of what is completed
    e_time = t.time()
    print('COMPLETED: ', file_nm, ' - ', e_time - s_time)
    fgp = open('GAMEPLAY.LOG', mode='a')
    fgp.write('COMPLETED: ' + file_nm + ' - ' + str(e_time - s_time) + '\n')
    fgp.close()

# Write Output File after converting entire list of dict to data frame
o1_time = t.time()
pd.DataFrame(gv.full_output).transpose().to_csv('OUTPUT.csv', sep=',', mode='w')

# WRITING OUTPUT PERFORMANCE
o2_time = t.time()
fgp = open('GAMEPLAY.LOG', mode='a')
fgp.write('Processing Games Output File: ' + str(o2_time - o1_time) + '\n')
print('Processing Games Output File: ', o2_time - o1_time)
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
fgp.write('Stats Processing: ' + str(t2_time - t1_time) + '\n')
print('Stats Processing: ', t2_time - t1_time)
fgp.close()
