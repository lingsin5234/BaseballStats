# extracting the data

# libraries
import pandas as pd
import re
import os
import sys
import game_converter as g
import play_processor as pp
import stat_collector as sc


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

output = sc.game_tracker(games, game_ids)
print(output[0])


# convert all games for 1 file
# a_full_df = g.convert_games(games)
# full_output = pd.DataFrame(columns=a_full_df[0].columns)

# play_processor2 function
# for e, each_game in enumerate(a_full_df):
#    new_output = pp.play_processor2(e+1, each_game)
#    full_output = full_output.append(new_output, ignore_index=True)

# write to file
# output_df.to_csv('OUTPUT.csv', sep=',', index=False)
# full_output.to_csv('OUTPUT.csv', sep=',', index=False)

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
