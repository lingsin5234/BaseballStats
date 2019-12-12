# libraries
import global_variables as gv
import pandas as pd


# stat collector
def stat_collector(player_id, game_id, stat_type, stat_value, actual_play):

    # modify player table
    gv.player.loc[-1] = [player_id, game_id, stat_type, stat_value, actual_play]
    gv.player.index = gv.player.index + 1

    return True


# stat organizer
def stat_organizer(player_tb):

    player_tb = player_tb.groupby(['player_id', 'stat_type']).size().reset_index()
    # a column named '0' will appear with all the values for each stat_type
    # this must be included as the "values" operator in the pivot function!
    player_tb = player_tb.pivot('player_id', 'stat_type', 0)
    player_tb = player_tb.fillna(0)
    player_tb = player_tb.astype(int)
    player_tb = pd.DataFrame(player_tb.to_records())

    return player_tb


# game start tracker
def game_tracker(all_starts, all_game_ids):

    # get all the game ids
    games_ids = pd.DataFrame(all_game_ids)
    games_ids[0] = games_ids[0].str.replace('\n', '')
    games_ids[0] = games_ids[0].str.replace('id,', '')

    # sort all the game starts
    games_dfs = pd.DataFrame()
    for g in range(len(all_starts)):
        # convert to table
        pdf = pd.DataFrame(all_starts[g][-2])  # 2nd last item is all starting lineups
        df1 = pd.concat([pdf[0].str.split(',', expand=True)], axis=1)

        # remove line break in last column
        df1[5] = df1[5].str.replace('\n', '')

        # table edits
        df1.drop(0, axis=1, inplace=True)
        df1.rename(columns={1: 'player_id', 2: 'player_nm', 3: 'team', 4: 'bat_lineup', 5: 'fielding'}, inplace=True)
        # df1.columns = ['player_id', 'player_nm', 'team', 'bat_lineup', 'fielding']

        # insert game_id column -- do not use df1 = df1.insert(...)
        df1.insert(0, 'game_id', games_ids.loc[g, 0])

        # add game starters to the table
        games_dfs = games_dfs.append(df1.copy())

    # reset the index
    games_dfs = games_dfs.reset_index(drop=True)

    return games_dfs