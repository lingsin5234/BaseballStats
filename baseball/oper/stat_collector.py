# libraries
from . import global_variables as gv
import pandas as pd
import time as t
from . import base_running as br
from . import date_time as dt
from sklearn.feature_extraction import DictVectorizer
import numpy as np
import json


# stat collector
def stat_collector(pid, lineup, the_line, stat_types):

    # game info values
    game_id = the_line['game_id']
    this_half = the_line['half_innings']
    actual_play = the_line['play']
    pitch_count = the_line['pitch_count']
    data_year = the_line['data_year']

    # get vis_team and home_team
    vis_team = lineup.loc[0, 'team_name']
    home_team = lineup.loc[10, 'team_name']

    # which team? find out in the_line
    if the_line['team_id'] == '0':
        team_name = vis_team  # visitor
        stat_team = 'VISIT'
    else:
        team_name = home_team  # home
        stat_team = 'HOME'

    # gather more information about the play
    num_outs = the_line['outs']

    # base runners
    bases_taken = br.bases_occupied(the_line)

    # get values for specific columns for the LOB, RLSP use
    bases_before = sum(c.isdigit() for c in bases_taken)
    scoring_pos = bases_taken.split('1')
    if len(scoring_pos) > 1:
        scoring_pos = sum(c.isdigit() for c in scoring_pos[1])
    else:
        scoring_pos = 0

    # for each stat_type, call stat_appender
    for s_type in stat_types:
        if s_type == 'LOB':
            lobs = bases_before - the_line['play'].count(r'-H')
            stat_appender(pid, team_name, data_year, game_id, this_half, s_type, lobs, actual_play, pitch_count,
                          num_outs, bases_taken, stat_team, 'batting')
        elif s_type == 'RLSP':
            rlsp = scoring_pos - the_line['play'].count(r'-H')
            if rlsp < 0:
                rlsp = 0
            stat_appender(pid, team_name, data_year, game_id, this_half, s_type, rlsp, actual_play, pitch_count,
                          num_outs, bases_taken, stat_team, 'batting')
        else:
            stat_appender(pid, team_name, data_year, game_id, this_half, s_type, 1, actual_play, pitch_count,
                          num_outs, bases_taken, stat_team, 'batting')

    return True


# stat appender
def stat_appender(player_id, team_name, data_year, game_id, this_half, stat_type, stat_value, actual_play,
                  pitch_count, num_outs, bases_taken, stat_team, bat_pitch):

    # store into player dict using the player_idx index
    gv.player[gv.player_idx] = {"player_id": player_id,
                                "team_name": team_name,
                                "data_year": data_year,
                                "game_id": game_id,
                                "this_half": this_half,
                                "stat_type": stat_type,
                                "stat_value": stat_value,
                                "actual_play": actual_play,
                                "pitch_count": pitch_count,
                                "num_outs": num_outs,
                                "bases_taken": bases_taken,
                                "stat_team": stat_team,
                                "bat_pitch": bat_pitch}
    gv.player_idx += 1  # increment index for next use

    # pujols tracker
    if player_id == 'pujoa001' and stat_type in ['A', 'PO', 'DP', 'TP', 'E']:
        gv.pujols_tracker[stat_type] += 1

    return True


# stat organizer
def stat_organizer(player_dict):

    # convert player_dict into table
    player_tb = pd.DataFrame.from_dict(player_dict, "index")
    player_tb.to_csv('PRE_STATS.csv', sep=',')
    # player_tb = player_dict

    # reshape the data
    player_tb = player_tb.groupby(['player_id', 'team_name', 'data_year', 'bat_pitch', 'stat_type'])\
        .agg({'stat_value': 'sum'}).reset_index()

    # set index to BOTH player_id and team_name and pivot based on stat_type column and values
    player_tb = player_tb.set_index(
        ['player_id', 'team_name', 'data_year', 'bat_pitch']).pivot(columns='stat_type')['stat_value']

    # reset index and rename to fix the structure of the columns
    player_tb = player_tb.reset_index().rename_axis(None, axis=1)
    player_tb = player_tb.fillna(0)
    # print(player_tb.head)

    # separate pitching, batting and fielding stats here
    stats_tb = {"pitching": player_tb[player_tb.bat_pitch == 'pitching'],
                "batting": player_tb[player_tb.bat_pitch == 'batting'],
                "fielding": player_tb[player_tb.bat_pitch == 'fielding']}
    # print(stats_tb)
    # only include relevant columns for each type of stat
    bat_col = ['player_id', 'team_name', 'data_year']
    bat_col.extend(list(gv.bat_stat_types.keys()))
    bat_col = [c for c in bat_col if c not in ['PID', 'YEAR', 'TEAM']]
    pitch_col = ['player_id', 'team_name', 'data_year']
    pitch_col.extend(list(gv.pitch_stat_types.keys()))
    pitch_col = [c for c in pitch_col if c not in ['PID', 'YEAR', 'TEAM']]
    field_col = ['player_id', 'team_name', 'data_year']
    field_col.extend(list(gv.field_stat_types.keys()))
    field_col = [c for c in field_col if c not in ['PID', 'YEAR', 'TEAM']]

    # if any of the stat types are missing, assign a random 0
    missing_bat_col = [b for b in bat_col if b not in stats_tb['batting'].columns]
    missing_pitch_col = [p for p in pitch_col if p not in stats_tb['pitching'].columns]
    missing_field_col = [p for p in field_col if p not in stats_tb['fielding'].columns]
    # print("Missing Columns", bat_col, missing_bat_col, pitch_col, missing_pitch_col)
    if len(missing_bat_col) > 0:
        for e in missing_bat_col:
            zeros = [0.0] * len(stats_tb['batting'])
            num_cols = int(stats_tb['batting'].count(axis=1).reset_index(drop=True)[0])  # defaults int64; index is off
            stats_tb['batting'].insert(num_cols, e, zeros, True)
    if len(missing_pitch_col) > 0:
        print(missing_pitch_col)
        for e in missing_pitch_col:
            zeros = [0.0] * len(stats_tb['pitching'])
            num_cols = int(stats_tb['pitching'].count(axis=1).reset_index(drop=True)[0])
            stats_tb['pitching'].insert(num_cols, e, zeros, True)
    if len(missing_field_col) > 0:
        print(missing_field_col)
        for e in missing_field_col:
            zeros = [0.0] * len(stats_tb['fielding'])
            num_cols = int(stats_tb['fielding'].count(axis=1).reset_index(drop=True)[0])
            stats_tb['fielding'].insert(num_cols, e, zeros, True)

    # assign the appropriate columns
    stats_tb['batting'] = stats_tb['batting'][bat_col]
    stats_tb['pitching'] = stats_tb['pitching'][pitch_col]
    stats_tb['fielding'] = stats_tb['fielding'][field_col]

    # no need to rename columns! :)
    print("RENAMING IN PROGRESS . . . ")
    stats_tb['batting'] = stats_tb['batting'].rename(
        columns={"player_id": 'PID', 'team_name': 'TEAM', 'data_year': 'YEAR'})
    stats_tb['pitching'] = stats_tb['pitching'].rename(
        columns={'player_id': 'PID', 'team_name': 'TEAM', 'data_year': 'YEAR'})
    stats_tb['fielding'] = stats_tb['fielding'].rename(
        columns={'player_id': 'PID', 'team_name': 'TEAM', 'data_year': 'YEAR'})

    # innings - divided into 3 outs
    floor_innings = stats_tb['pitching']['IP'] // 3
    modulus_innings = stats_tb['pitching']['IP'] % 3 / 10
    stats_tb['pitching']['IP'] = floor_innings + modulus_innings
    floor_innings = stats_tb['fielding']['IP'] // 3
    modulus_innings = stats_tb['fielding']['IP'] % 3 / 10
    stats_tb['fielding']['IP'] = floor_innings + modulus_innings

    # quick checks
    # print(stats_tb['batting'].head)
    # print(stats_tb['pitching'].head)
    # print(stats_tb['fielding'].head)

    return stats_tb


# game start tracker
def game_tracker(all_starts, data_year):

    # convert to dictionary
    games_dict = {}
    for g in range(len(all_starts)):
        # get team and lineup info
        game_id = all_starts[g][0].split(',')[1].split('\n')[0]
        vis_team = all_starts[g][2].split(',')[2].split('\n')[0]
        home_team = all_starts[g][3].split(',')[2].split('\n')[0]
        lineups = all_starts[g][-2]  # 2nd last item is all starting lineups

        # push lineup into dictionary
        for starter in lineups:

            ss = starter.split('\n')[0].split(',')
            if ss[3] == '0':
                team_nm = vis_team
            else:
                team_nm = home_team
            lineup_dict = {'game_id': game_id,
                           'data_year': data_year,
                           'player_id': ss[1],
                           'player_nm': ss[2].replace('"', ''),
                           'team_id': ss[3],
                           'team_name': team_nm,
                           'bat_lineup': ss[4],
                           'fielding': ss[5]}
            games_dict[gv.gr_idx] = lineup_dict
            gv.gr_idx += 1

            # stat appender
            if int(ss[4]) > 0:  # batter excluding AL pitchers
                stat_appender(ss[1], team_nm, data_year, game_id, 0, 'GS', 1, None, None, 0, '---', ss[3], 'batting')
                stat_appender(ss[1], team_nm, data_year, game_id, 0, 'GP', 1, None, None, 0, '---', ss[3], 'batting')
            if int(ss[5]) == 1:  # pitcher
                stat_appender(ss[1], team_nm, data_year, game_id, 0, 'GS', 1, None, None, 0, '---', ss[3], 'pitching')
                stat_appender(ss[1], team_nm, data_year, game_id, 0, 'GP', 1, None, None, 0, '---', ss[3], 'pitching')
            if int(ss[5]) < 10:  # not DH PH PR, is a fielder
                stat_appender(ss[1], team_nm, data_year, game_id, 0, 'GS', 1, None, None, 0, '---', ss[3], 'fielding')
                stat_appender(ss[1], team_nm, data_year, game_id, 0, 'GP', 1, None, None, 0, '---', ss[3], 'fielding')

    return games_dict


# in order to split the generate stats function into separate batting, fielding and pitching jobs
# need to split the stat_organizer into separate functions
def stat_organizer2(player_dict, stat_category):

    # convert player_dict into table
    # player_tb = pd.DataFrame.from_dict(player_dict, "index")
    # player_tb.to_csv('PRE_STATS.csv', sep=',')
    t1 = t.time()
    # pd.json_normalize
    p_dict = [v for (k, v) in list(player_dict.items())]
    player_tb = pd.json_normalize(p_dict, meta=list(p_dict[0].keys()))
    # print(player_tb.head())
    t2 = t.time()
    # reshape the data
    player_tb = player_tb.groupby(['player_id', 'team_name', 'data_year', 'bat_pitch', 'stat_type'])\
        .agg({'stat_value': 'sum'}).reset_index()
    t3 = t.time()
    # set index to BOTH player_id and team_name and pivot based on stat_type column and values
    player_tb = player_tb.set_index(
        ['player_id', 'team_name', 'data_year', 'bat_pitch']).pivot(columns='stat_type')['stat_value']
    t4 = t.time()
    # reset index and rename to fix the structure of the columns
    player_tb = player_tb.reset_index().rename_axis(None, axis=1)
    t5 = t.time()
    player_tb = player_tb.fillna(0)
    # print(player_tb.head)
    t6 = t.time()
    # separate pitching, batting and fielding stats here
    stats_tb = {"pitching": player_tb[player_tb.bat_pitch == 'pitching'],
                "batting": player_tb[player_tb.bat_pitch == 'batting'],
                "fielding": player_tb[player_tb.bat_pitch == 'fielding']}

    # only include relevant columns for each type of stat
    stat_col = ['player_id', 'team_name', 'data_year']
    if stat_category == 'batting':
        stat_col.extend(list(gv.bat_stat_types.keys()))
    elif stat_category == 'pitching':
        stat_col.extend(list(gv.pitch_stat_types.keys()))
    elif stat_category == 'fielding':
        stat_col.extend(list(gv.field_stat_types.keys()))
    stat_col = [c for c in stat_col if c not in ['PID', 'YEAR', 'TEAM']]
    t7 = t.time()
    # if any of the stat types are missing, assign 0
    missing_stat_col = [b for b in stat_col if b not in stats_tb[stat_category].columns]
    if len(missing_stat_col) > 0:
        for e in missing_stat_col:
            zeros = [0.0] * len(stats_tb[stat_category])
            num_cols = int(stats_tb[stat_category].count(axis=1).reset_index(drop=True)[0])
            stats_tb[stat_category].insert(num_cols, e, zeros, True)
    t8 = t.time()
    # assign the appropriate columns
    stats_tb[stat_category] = stats_tb[stat_category][stat_col]
    t9 = t.time()
    # no need to rename columns! :)
    # print("RENAMING IN PROGRESS . . . ")
    stats_tb[stat_category] = stats_tb[stat_category].rename(
        columns={"player_id": 'PID', 'team_name': 'TEAM', 'data_year': 'YEAR'})
    t10 = t.time()
    # innings - divided into 3 outs
    if stat_category in ['pitching', 'fielding']:
        floor_innings = stats_tb[stat_category]['IP'] // 3
        modulus_innings = stats_tb[stat_category]['IP'] % 3 / 10
        stats_tb[stat_category]['IP'] = floor_innings + modulus_innings
    t11 = t.time()

    # quick checks
    # print(stats_tb[stat_category].head)

    dict_times = {
        'json_normalize': dt.seconds_convert(t2 - t1),
        'groupby agg': dt.seconds_convert(t3 - t2),
        'set_index pivot': dt.seconds_convert(t4 - t3),
        'reset_index rename_axis': dt.seconds_convert(t5 - t4),
        'fillna': dt.seconds_convert(t6 - t5),
        'extend_stat_types': dt.seconds_convert(t7 - t6),
        'assign_0s': dt.seconds_convert(t8 - t7),
        'assign_cols': dt.seconds_convert(t9 - t8),
        'rename_cols': dt.seconds_convert(t10 - t9),
        'innings_calc': dt.seconds_convert(t11 - t10)
    }

    # for k, v in enumerate(dict_times):
    #     print(v, dict_times[v])

    return stats_tb



