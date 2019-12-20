# libraries
import global_variables as gv
import pandas as pd
import time as t


# stat collector
def stat_collector(pid, the_line, stat_types):

    # game info values
    game_id = the_line['game_id'].values[0]
    this_half = the_line['half_innings'].values[0]
    actual_play = the_line['play'].values[0]

    # get vis_team and home_team
    curr_game = gv.game_roster.game_id == game_id
    vis_team = gv.game_roster.loc[curr_game, 'team_name'].values[0]
    home_team = gv.game_roster.loc[curr_game, 'team_name'].values[-1]

    # which team? find out in the_line
    if the_line['team_id'].values[0] == '0':
        team_name = vis_team  # visitor
    else:
        team_name = home_team  # home

    # constants - specific columns for the LOB, RLSP use
    bases_before = ['1B_before', '2B_before', '3B_before']
    scoring_pos = ['2B_before', '3B_before']

    # for each stat_type, call stat_appender
    for s_type in stat_types:
        if s_type == 'LOB':
            lobs = the_line[bases_before].count().sum() - the_line['play'].values[0].count(r'-H')
            stat_appender(pid, team_name, game_id, this_half, s_type, lobs, actual_play)
        elif s_type == 'RLSP':
            rlsp = the_line[scoring_pos].count().sum() - the_line['play'].values[0].count(r'-H')
            if rlsp < 0:
                rlsp = 0
            stat_appender(pid, team_name, game_id, this_half, s_type, rlsp, actual_play)
        else:
            stat_appender(pid, team_name, game_id, this_half, s_type, 1, actual_play)

    return True


# stat appender
def stat_appender(player_id, team_name, game_id, this_half, stat_type, stat_value, actual_play):

    # store into player dict using the player_idx index
    gv.player[gv.player_idx] = {"player_id": player_id,
                                "team_name": team_name,
                                "game_id": game_id,
                                "this_half": this_half,
                                "stat_type": stat_type,
                                "stat_value": stat_value,
                                "actual_play": actual_play}
    gv.player_idx += 1  # increment index for next use
    return True


# stat organizer
def stat_organizer(player_dict):

    # convert player_dict into table
    player_tb = pd.DataFrame.from_dict(player_dict, "index")
    print(player_tb)
    exit()

    player_tb = player_tb.groupby(['player_id', 'team_name', 'stat_type']).size().reset_index()
    # rename the "0" column to values
    player_tb.rename(columns={0: 'values'}, inplace=True)
    # set index to BOTH player_id and team_name and pivot based on stat_type column and values
    player_tb = player_tb.set_index(['player_id', 'team_name']).pivot(columns='stat_type')['values']
    # reset index and rename to fix the structure of the columns
    player_tb = player_tb.reset_index().rename_axis(None, axis=1)
    player_tb = player_tb.fillna(0)
    # player_tb = player_tb.astype(int)
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
        # get the visiting and home teams
        vis_team = all_starts[g][2]
        home_team = all_starts[g][3]

        # convert to table
        pdf = pd.DataFrame(all_starts[g][-2])  # 2nd last item is all starting lineups
        df1 = pd.concat([pdf[0].str.split(',', expand=True)], axis=1)

        # remove line break in last column
        df1[5] = df1[5].str.replace('\n', '')

        # insert team_name
        df1.insert(6, 6, '0')

        # table edits
        df1.drop(0, axis=1, inplace=True)
        df1.rename(columns={1: 'player_id', 2: 'player_nm', 3: 'team_id', 4: 'team_name',
                            5: 'bat_lineup', 6: 'fielding'}, inplace=True)
        # df1.columns = ['player_id', 'player_nm', 'team', 'bat_lineup', 'fielding']

        # insert game_id column -- do not use df1 = df1.insert(...)
        df1.insert(0, 'game_id', games_ids.loc[g, 0])

        # replace 0 with vis_team; 1 with home_team
        df1.loc[df1.team_id == '0', 'team_name'] = vis_team.replace('info,visteam,', '').replace('\n', '')
        df1.loc[df1.team_id == '1', 'team_name'] = home_team.replace('info,hometeam,', '').replace('\n', '')

        # add game starters to the table
        games_dfs = games_dfs.append(df1.copy())

    # reset the index
    games_dfs = games_dfs.reset_index(drop=True)

    return games_dfs

