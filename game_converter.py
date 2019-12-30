# libraries
import time as t
import global_variables as gv


# convert play by play to tables
def convert_games(all_games):

    # get game id from game_rosters
    game_id = gv.game_roster.game_id.unique()

    games_dfs = []
    for g, each_game in enumerate(all_games):

        # performance
        g1_time = t.time()

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
                       'type': i[0],
                       'inning': i[1],
                       'half': i[2],
                       'half_inning': i[1] + '_' + i[2],
                       'playerID': i[3],
                       'count': i[4],
                       'pitches': i[5],
                       'play': i[6],
                       'name': None,
                       'team_id': i[2],
                       'team_name': None,
                       'batting': None,
                       'fielding': None,
                       'pitcherID': None,
                       'outs': 0,
                       '1B_before': None,
                       '2B_before': None,
                       '3B_before': None,
                       '1B_after': None,
                       '2B_after': None,
                       '3B_after': None,
                       'runs_scored': 0,
                       'total_scored': 0}
            else:
                dct = {'game_id': game_id[g],
                       'type': i[0],
                       'inning': None,
                       'half': None,
                       'half_inning': None,
                       'playerID': i[1],
                       'count': None,
                       'pitches': None,
                       'play': None,
                       'name': i[2],
                       'team_id': i[3],
                       'team_name': None,
                       'batting': i[4],
                       'fielding': i[5],
                       'pitcherID': None,
                       'outs': 0,
                       '1B_before': None,
                       '2B_before': None,
                       '3B_before': None,
                       '1B_after': None,
                       '2B_after': None,
                       '3B_after': None,
                       'runs_scored': 0,
                       'total_scored': 0}
            game_dict[idx] = dct
            idx += 1

        games_dfs.append(game_dict)

        # performance
        g2_time = t.time()
        print('Game:', g, g2_time - g1_time)

    return games_dfs
