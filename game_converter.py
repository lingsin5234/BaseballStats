# libraries
import pandas as pd


# convert play by play to tables
def convert_games(all_games):

    games_dfs = []
    for g in range(len(all_games)):

        # convert to table
        pdf = pd.DataFrame(all_games[g][-1])  # last item is entire game_play
        df1 = pd.concat([pdf[0].str.split(',', expand=True)], axis=1)

        # remove line break in last column
        df1[6] = df1[6].str.replace('\n', '')

        # add some column names with some extra ones too
        df1.columns = ['type', 'inning', 'half', 'playerID', 'count', 'pitches', 'play']

        # add newer columns
        df1.insert(7, 'name', None)
        df1.insert(8, 'team', None)
        df1.insert(9, 'batting', None)
        df1.insert(10, 'fielding', None)

        # shift the substitutions into newer columns
        df1.loc[df1.type == 'sub', 'name'] = df1.loc[df1.type == 'sub', 'half'].tolist()
        df1.loc[df1.type == 'sub', 'team'] = df1.loc[df1.type == 'sub', 'playerID'].tolist()
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

        # add outs and baserunners columns
        df1.insert(11, 'outs', 0)
        df1.insert(12, '1B_before', None)
        df1.insert(13, '2B_before', None)
        df1.insert(14, '3B_before', None)
        df1.insert(15, '1B_after', None)
        df1.insert(16, '2B_after', None)
        df1.insert(17, '3B_after', None)
        df1.insert(18, 'runs_scored', 0)
        df1.insert(19, 'total_runs', 0)

        # insert half innings
        df1.insert(3, 'half_innings', None)
        df1.half_innings = df1.inning + '_' + df1.half

        # add to full game_dfs list
        games_dfs.append(df1.copy())
        # print(g, ': ', len(games_dfs), ' df: ', len(df1))

    return games_dfs
