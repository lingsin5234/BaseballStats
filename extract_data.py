# extracting the data

# libraries
import pandas as pd
import re
import os
import sys
import game_converter as g
import play_processor as pp
import stat_collector as sc
import global_variables as gv


# get argument
year_range = sys.argv[1]

# check if range or single
if re.search(r'^(19[0-9][0-9]|20[01][0-9])-(19[0-9][0-9]|20[01][0-9])$', year_range):
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
file_dir = dir_str + '/2016TOR.EVA'
f = open(file_dir, "r")
f1 = f.readlines()
# print(event_file)

# collect id and group the games
games = []
game_ids = []
game_info = []
game_play = []
game_start = []
for line_item in f1:
    if line_item[:2] == "id":

        # append game id
        game_ids.append(line_item)

        # populate game info, starts, plays
        if len(game_info) > 0:
            game_info.append(game_start.copy())
            game_info.append(game_play.copy())
            games.append(game_info.copy())
        game_info.clear()
        game_start.clear()
        game_play.clear()  # Needed to clear this so it doesn't tack on for all remaining games!
        game_info.append(line_item)
    elif line_item[:4] == "play" or line_item[:3] == "sub":
        game_play.append(line_item)
    elif line_item[:5] == "start":
        game_start.append(line_item)
    else:
        game_info.append(line_item)

# extract all starting lineups
gv.game_roster = sc.game_tracker(games, game_ids)
gv.game_roster.to_csv('STARTERS.csv', sep=',', index=False)

# convert all games for 1 file
a_full_df = g.convert_games(games)
full_output = pd.DataFrame(columns=a_full_df[0].columns)

# play_processor2 function
for e, each_game in enumerate(a_full_df):
    # add the game_ids first
    current_game_id = game_ids[e].replace('\n', '')
    current_game_id = current_game_id.replace('id,', '')
    each_game.insert(0, 'game_id', current_game_id)

    # then run the processor
    new_output = pp.play_processor2(e+1, each_game)
    full_output = full_output.append(new_output, sort=False)

# reindex the columns once
full_output = full_output.reindex(new_output.columns, axis=1)

# write to file
full_output.to_csv('OUTPUT.csv', sep=',', index=False)

# player stats
# print(player.groupby(['player_id', 'stat_type']).size().reset_index())
# print(player)
# player_stats = stat_organizer(player)
# player_stats.to_csv('STATS.csv', sep=',', index=False)

player_stats = pd.read_csv('STATS.csv')
player_stats = player_stats.pivot('player_id', 'stat_type')
player_stats = player_stats.fillna(0)
player_stats = player_stats.astype(int)
# print(player_stats)
