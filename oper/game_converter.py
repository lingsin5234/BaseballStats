# libraries
import time as t
from . import global_variables as gv


# convert play by play to tables
def convert_games(all_games, games_roster):

    # get game id from game_rosters
    game_id = games_roster.game_id.unique()
    year = games_roster.data_year.unique()[0]

    games_dfs = []
    for g, each_game in enumerate(all_games):

        # convert to dictionary
        game_dict = {}
        idx = 0

        # remove \n, then split by comma
        this_list = [i.split('\n')[0] for i in each_game[-1]]
        this_list = [i.split(',') for i in this_list]

        # loop through and assign dict value
        for i in this_list:
            if i[0] == 'play':
                dct = {'game_id': game_id[g],
                       'data_year': year,
                       'gm_type': i[0],
                       'inning': i[1],
                       'half': i[2],
                       'half_innings': i[1] + '_' + i[2],
                       'playerID': i[3],
                       'pitch_count': i[4],
                       'pitches': i[5],
                       'play': i[6],
                       'player_name': None,
                       'team_id': i[2],
                       'team_name': None,
                       'batting': None,
                       'fielding': None,
                       'pitcherID': None,
                       'outs': 0,
                       'before_1B': None,
                       'before_2B': None,
                       'before_3B': None,
                       'after_1B': None,
                       'after_2B': None,
                       'after_3B': None,
                       'runs_scored': 0,
                       'total_scored': 0}
            else:
                dct = {'game_id': game_id[g],
                       'data_year': year,
                       'gm_type': i[0],
                       'inning': None,
                       'half': None,
                       'half_innings': None,
                       'playerID': i[1],
                       'pitch_count': None,
                       'pitches': None,
                       'play': None,
                       'player_name': i[2],
                       'team_id': i[3],
                       'team_name': None,
                       'batting': i[4],
                       'fielding': i[5],
                       'pitcherID': None,
                       'outs': 0,
                       'before_1B': None,
                       'before_2B': None,
                       'before_3B': None,
                       'after_1B': None,
                       'after_2B': None,
                       'after_3B': None,
                       'runs_scored': 0,
                       'total_scored': 0}
            game_dict[idx] = dct
            idx += 1

        games_dfs.append(game_dict)

    return games_dfs
