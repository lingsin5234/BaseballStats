# libraries
import pandas as pd
import time as t


# convert play by play to tables
def convert_games(all_games):

    games_dfs = []
    for g in range(len(all_games)):

        #  ## performance analysis: DICTIONARY ##
        d1_time = t.time()

        # convert to dictionary
        game_dict = {}
        idx = 0

        # remove \n, then split by comma
        this_list = [i.split('\n')[0] for i in all_games[g][-1]]
        this_list = [i.split(',') for i in this_list]

        # loop through and assign dict value
        for i in this_list:
            if i[0] == 'play':
                dct = {'type': i[0],
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
                dct = {'type': i[0],
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

        print(game_dict)
        print(len(game_dict[88]))
        print(len(game_dict[90]))

        #  ## performance analysis: DICTIONARY ##
        d2_time = t.time()

        #  ## performance analysis: DATA FRAME ##
        t1_time = t.time()

        # convert to table
        pdf = pd.DataFrame(all_games[g][-1])  # last item is entire game_play
        df1 = pd.concat([pdf[0].str.split(',', expand=True)], axis=1)

        # remove line break in last column
        df1[6] = df1[6].str.replace('\n', '')

        # add some column names with some extra ones too
        df1.columns = ['type', 'inning', 'half', 'playerID', 'count', 'pitches', 'play']

        # add newer columns
        df1.insert(7, 'name', None)
        df1.insert(8, 'team_id', None)
        df1.insert(9, 'team_name', None)
        df1.insert(10, 'batting', None)
        df1.insert(11, 'fielding', None)
        df1.insert(12, 'pitcherID', None)

        # shift the substitutions into newer columns
        df1.loc[df1.type == 'sub', 'name'] = df1.loc[df1.type == 'sub', 'half'].tolist()
        df1.loc[df1.type == 'sub', 'team_id'] = df1.loc[df1.type == 'sub', 'playerID'].tolist()
        df1.loc[df1.type == 'sub', 'batting'] = df1.loc[df1.type == 'sub', 'count'].tolist()
        df1.loc[df1.type == 'sub', 'fielding'] = df1.loc[df1.type == 'sub', 'pitches'].tolist()

        # correct the remaining columns
        df1.loc[df1.type == 'sub', 'playerID'] = df1.loc[df1.type == 'sub', 'inning']
        df1.loc[df1.type == 'sub', 'count'] = None
        df1.loc[df1.type == 'sub', 'pitches'] = None

        # using current index to retrieve and replace with -1 index with inning and half inning values
        previous_index = df1[df1.type == 'sub'].index.values - 1
        df1.loc[df1.type == 'sub', 'inning'] = df1.loc[previous_index, 'inning'].tolist()
        df1.loc[df1.type == 'sub', 'half'] = df1.loc[previous_index, 'half'].tolist()

        # remove line break in last column for subs
        df1.loc[df1.type == 'sub', 'fielding'] = df1.loc[df1.type == 'sub', 'fielding'].str.replace('\n', '').tolist()

        # replace all blank "team" with the half - to determine the team that is at bat
        df1.loc[df1.team_id.isnull(), 'team_id'] = df1.loc[df1.team_id.isnull(), 'half']

        # add outs and baserunners columns
        df1.insert(13, 'outs', 0)
        df1.insert(14, '1B_before', None)
        df1.insert(15, '2B_before', None)
        df1.insert(16, '3B_before', None)
        df1.insert(17, '1B_after', None)
        df1.insert(18, '2B_after', None)
        df1.insert(19, '3B_after', None)
        df1.insert(20, 'runs_scored', 0)
        df1.insert(21, 'total_runs', 0)

        # insert half innings
        df1.insert(3, 'half_innings', None)
        df1.half_innings = df1.inning + '_' + df1.half

        #  ## performance analysis: DATA FRAME ##
        t2_time = t.time()

        # ## performance analysis results ##
        print('DICTIONARY: ', d2_time - d1_time)
        print('DATA FRAME: ', t2_time - t1_time)
        exit()
        # add to full game_dfs list
        games_dfs.append(df1.copy())
        # print(g, ': ', len(games_dfs), ' df: ', len(df1))

    return games_dfs
