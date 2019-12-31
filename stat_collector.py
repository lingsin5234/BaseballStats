# libraries
import global_variables as gv
import pandas as pd
import time as t


# stat collector
def stat_collector(pid, lineup, the_line, stat_types):

    # game info values
    game_id = the_line['game_id']
    this_half = the_line['half_innings']
    actual_play = the_line['play']

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
    bases_taken = []
    if the_line['1B_before']:
        bases_taken.append('1')
    else:
        bases_taken.append('-')
    if the_line['2B_before']:
        bases_taken.append('2')
    else:
        bases_taken.append('-')
    if the_line['3B_before']:
        bases_taken.append('3')
    else:
        bases_taken.append('-')
    bases_taken = ''.join(map(str, bases_taken))

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
            stat_appender(pid, team_name, game_id, this_half, s_type, lobs, actual_play, num_outs, bases_taken,
                          stat_team, 'batting')
        elif s_type == 'RLSP':
            rlsp = scoring_pos - the_line['play'].count(r'-H')
            if rlsp < 0:
                rlsp = 0
            stat_appender(pid, team_name, game_id, this_half, s_type, rlsp, actual_play, num_outs, bases_taken,
                          stat_team, 'batting')
        else:
            stat_appender(pid, team_name, game_id, this_half, s_type, 1, actual_play, num_outs, bases_taken,
                          stat_team, 'batting')

    return True


# stat appender
def stat_appender(player_id, team_name, game_id, this_half, stat_type, stat_value, actual_play,
                  num_outs, bases_taken, stat_team, bat_pitch):

    # store into player dict using the player_idx index
    gv.player[gv.player_idx] = {"player_id": player_id,
                                "team_name": team_name,
                                "game_id": game_id,
                                "this_half": this_half,
                                "stat_type": stat_type,
                                "stat_value": stat_value,
                                "actual_play": actual_play,
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
    player_tb = player_tb.groupby(['player_id', 'team_name', 'bat_pitch', 'stat_type']).size().reset_index()

    # rename the "0" column to values
    player_tb.rename(columns={0: 'values'}, inplace=True)
    # set index to BOTH player_id and team_name and pivot based on stat_type column and values
    player_tb = player_tb.set_index(['player_id', 'team_name', 'bat_pitch']).pivot(columns='stat_type')['values']

    # reset index and rename to fix the structure of the columns
    player_tb = player_tb.reset_index().rename_axis(None, axis=1)
    player_tb = player_tb.fillna(0)

    # separate pitching, batting and fielding stats here
    stats_tb = {"pitching": player_tb[player_tb.bat_pitch == 'pitching'],
                "batting": player_tb[player_tb.bat_pitch == 'batting']}

    # only include relevant columns for each type of stat
    bat_col = ['player_id', 'team_name']
    bat_col.extend(list(gv.bat_stats.keys()))
    pitch_col = ['player_id', 'team_name']
    pitch_col.extend(list(gv.pitch_stats.keys()))

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
            if ss[4] > 0:  # batter excluding AL pitchers
                stat_appender(ss[1], team_nm, game_id, 0, 'GS', 1, None, 0, '---', ss[3], 'batting')
            if ss[5] == 1:  # pitcher
                stat_appender(ss[1], team_nm, game_id, 0, 'GS', 1, None, 0, '---', ss[3], 'pitching')
            if ss[5] < 10:  # not DH PH PR, is a fielder
                stat_appender(ss[1], team_nm, game_id, 0, 'GS', 1, None, 0, '---', ss[3], 'fielding')

    return games_dict

