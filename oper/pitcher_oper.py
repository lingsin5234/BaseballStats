# libraries
from . import stat_collector as sc
from . import global_variables as gv
import re

# constant
max_pitch = 30  # maximum pitches thrown in at-bat, in case it ever gets beaten!


# assign the pitcher
def assign_pitcher(lineup, this_line):

    # check which team is batting
    if this_line['team_id'] == '0':
        pitch_team = '1'
    else:
        pitch_team = '0'

    # filter the corresponding pitcher_id
    pitch_filter = (lineup.team_id == pitch_team) & (lineup.fielding == '1')
    pitch_index = lineup.index[pitch_filter]
    if bool(len(pitch_index) == 0) & bool(this_line['play'] == 'NP'):
        pitcher_id = None
    elif bool(len(pitch_index) > 0):
        pitcher_id = lineup.at[pitch_index[0], 'player_id']
    else:
        print(lineup)
        print(this_line)
        print('Error with Assign Pitcher where the play is not "NP".')
        exit()

    return pitcher_id


# pitching stats collector
def pitch_collector(hid, lineup, the_line, stat_types):

    # get game info
    game_info = pitch_get_game_info(lineup, the_line)
    team_name, game_id, this_half, actual_play, \
        num_outs, bases_taken, stat_team = game_info
    pitch_count = the_line['pitch_count']
    data_year = the_line['data_year']

    # for each stat_type, call stat_appender
    for s_type in stat_types:
        sc.stat_appender(hid, team_name, data_year, game_id, this_half, s_type, 1, actual_play, pitch_count,
                         num_outs, bases_taken, stat_team, 'pitching')

    return True


# game info for pitcher collectors
def pitch_get_game_info(lineup, the_line):

    # game info values
    game_id = the_line['game_id']
    this_half = the_line['half_innings']
    actual_play = the_line['play']

    # get vis_team and home_team
    vis_team = lineup.loc[0, 'team_name']
    home_team = lineup.loc[10, 'team_name']

    # which team? find out in the_line -- THIS IS OPPOSITE to stat_collector!
    if the_line['half'] == '0':
        team_name = home_team  # home is pitching
        stat_team = 'HOME'
    else:
        team_name = vis_team  # visitor is pitching
        stat_team = 'VISIT'

    # gather more information about the play
    num_outs = the_line['outs']

    # base runners
    bases_taken = []
    if the_line['before_1B']:
        bases_taken.append('1')
    else:
        bases_taken.append('-')
    if the_line['before_2B']:
        bases_taken.append('2')
    else:
        bases_taken.append('-')
    if the_line['before_3B']:
        bases_taken.append('3')
    else:
        bases_taken.append('-')
    bases_taken = ''.join(map(str, bases_taken))

    return [team_name, game_id, this_half, actual_play, num_outs, bases_taken, stat_team]


# pitch count collector
def pitch_count_collector(pitcherID, playerID, lineup, the_line):

    # get game info
    game_info = pitch_get_game_info(lineup, the_line)
    team_name, game_id, this_half, actual_play, \
        num_outs, bases_taken, stat_team = game_info
    pitch_count = the_line['pitch_count']
    data_year = the_line['data_year']

    # the pitches
    pc = the_line['pitches']

    # pitches thrown - ignore N for no pitch
    thrown = re.subn('[A-MO-Z]', '', pc, max_pitch)[1]

    # strikes thrown
    strikes = re.subn('[CFKLMOQRSTXY]', '', pc, max_pitch)[1]

    # foul balls
    fouls = re.subn('[FLORT]', '', pc, max_pitch)[1]

    # balls thrown
    balls = re.subn('[BIPV]', '', pc, max_pitch)[1]

    # unknown or missed pitch - U

    # call stat_appender for PT, ST, FL, BT
    sc.stat_appender(pitcherID, team_name, data_year, game_id, this_half, 'PT', thrown, actual_play, pitch_count,
                     num_outs, bases_taken, stat_team, 'pitching')
    sc.stat_appender(pitcherID, team_name, data_year, game_id, this_half, 'ST', strikes, actual_play, pitch_count,
                     num_outs, bases_taken, stat_team, 'pitching')
    sc.stat_appender(pitcherID, team_name, data_year, game_id, this_half, 'FL', fouls, actual_play, pitch_count,
                     num_outs, bases_taken, stat_team, 'pitching')
    sc.stat_appender(pitcherID, team_name, data_year, game_id, this_half, 'BT', balls, actual_play, pitch_count,
                     num_outs, bases_taken, stat_team, 'pitching')

    return True
