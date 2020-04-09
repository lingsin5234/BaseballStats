# libraries
from . import global_variables as gv
import pandas as pd
import time as t
from . import base_running as br


# stat collector
def stat_collector(pid, lineup, the_line, stat_types):

    # game info values
    game_id = the_line['game_id']
    this_half = the_line['half_innings']
    actual_play = the_line['play']
    pitch_count = the_line['pitch_count']

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
            stat_appender(pid, team_name, game_id, this_half, s_type, lobs, actual_play, pitch_count,
                          num_outs, bases_taken, stat_team, 'batting')
        elif s_type == 'RLSP':
            rlsp = scoring_pos - the_line['play'].count(r'-H')
            if rlsp < 0:
                rlsp = 0
            stat_appender(pid, team_name, game_id, this_half, s_type, rlsp, actual_play, pitch_count,
                          num_outs, bases_taken, stat_team, 'batting')
        else:
            stat_appender(pid, team_name, game_id, this_half, s_type, 1, actual_play, pitch_count,
                          num_outs, bases_taken, stat_team, 'batting')

    return True


# stat appender
def stat_appender(player_id, team_name, game_id, this_half, stat_type, stat_value, actual_play,
                  pitch_count, num_outs, bases_taken, stat_team, bat_pitch):

    # store into player dict using the player_idx index
    gv.player[gv.player_idx] = {"player_id": player_id,
                                "team_name": team_name,
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
    return True


# stat organizer
def stat_organizer(player_dict):

    # convert player_dict into table
    player_tb = pd.DataFrame.from_dict(player_dict, "index")
    player_tb.to_csv('PRE_STATS.csv', sep=',')
    # player_tb = player_dict

    # reshape the data
    player_tb = player_tb.groupby(['player_id', 'team_name', 'bat_pitch', 'stat_type'])\
        .agg({'stat_value': 'sum'}).reset_index()

    # set index to BOTH player_id and team_name and pivot based on stat_type column and values
    player_tb = player_tb.set_index(['player_id', 'team_name', 'bat_pitch']).pivot(columns='stat_type')['stat_value']

    # reset index and rename to fix the structure of the columns
    player_tb = player_tb.reset_index().rename_axis(None, axis=1)
    player_tb = player_tb.fillna(0)
    print(player_tb)

    # separate pitching, batting and fielding stats here
    stats_tb = {"pitching": player_tb[player_tb.bat_pitch == 'pitching'],
                "batting": player_tb[player_tb.bat_pitch == 'batting']}
    print(stats_tb)
    # only include relevant columns for each type of stat
    bat_col = ['player_id', 'team_name']
    bat_col.extend(list(gv.bat_stat_types.keys()))
    pitch_col = ['player_id', 'team_name']
    pitch_col.extend(list(gv.pitch_stat_types.keys()))

    # if any of the stat types are missing, assign a random 0
    missing_bat_col = [b for b in bat_col if b not in stats_tb['batting'].columns]
    missing_pitch_col = [p for p in pitch_col if p not in stats_tb['pitching'].columns]
    print("Missing Columns", bat_col, missing_bat_col, pitch_col, missing_pitch_col)
    if len(missing_bat_col) > 0:
        for e in missing_bat_col:
            zeros = [0.0] * len(stats_tb['batting'])
            stats_tb['batting'][e] = zeros
    if len(missing_pitch_col) > 0:
        for e in missing_pitch_col:
            zeros = [0.0] * len(stats_tb['pitching'])
            stats_tb['pitching'][e] = zeros

    # re-assign the PID and TEAM correctly
    stats_tb['batting']['PID'] = stats_tb['batting']['player_id']
    stats_tb['batting']['TEAM'] = stats_tb['batting']['team_name']
    stats_tb['pitching']['PID'] = stats_tb['pitching']['player_id']
    stats_tb['pitching']['TEAM'] = stats_tb['pitching']['team_name']

    # assign the appropriate columns
    stats_tb['batting'] = stats_tb['batting'][bat_col]
    stats_tb['pitching'] = stats_tb['pitching'][pitch_col]

    # innings - divided into 3 outs
    floor_innings = stats_tb['pitching']['IP'] // 3
    modulus_innings = stats_tb['pitching']['IP'] % 3 / 10
    stats_tb['pitching']['IP'] = floor_innings + modulus_innings

    return stats_tb


# game start tracker
def game_tracker(all_starts):

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
                           'player_id': ss[1],
                           'player_nm': ss[2],
                           'team_id': ss[3],
                           'team_name': team_nm,
                           'bat_lineup': ss[4],
                           'fielding': ss[5]}
            games_dict[gv.gr_idx] = lineup_dict
            gv.gr_idx += 1

            # stat appender
            if int(ss[4]) > 0:  # batter excluding AL pitchers
                stat_appender(ss[1], team_nm, game_id, 0, 'GS', 1, None, None, 0, '---', ss[3], 'batting')
                stat_appender(ss[1], team_nm, game_id, 0, 'GP', 1, None, None, 0, '---', ss[3], 'batting')
            if int(ss[5]) == 1:  # pitcher
                stat_appender(ss[1], team_nm, game_id, 0, 'GS', 1, None, None, 0, '---', ss[3], 'pitching')
                stat_appender(ss[1], team_nm, game_id, 0, 'GP', 1, None, None, 0, '---', ss[3], 'pitching')
            if int(ss[5]) < 10:  # not DH PH PR, is a fielder
                stat_appender(ss[1], team_nm, game_id, 0, 'GS', 1, None, None, 0, '---', ss[3], 'fielding')
                stat_appender(ss[1], team_nm, game_id, 0, 'GP', 1, None, None, 0, '---', ss[3], 'fielding')

    return games_dict

