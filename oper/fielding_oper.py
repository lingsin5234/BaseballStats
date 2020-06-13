# libraries
from . import global_variables as gv
from . import stat_collector as sc
from . import base_running as br


# fielding substitutions
def lineup_substitution(this_line, lineup, pid, sub_type, field_pos):

    # by default, all substitutions are new except when handling Fielding Subs
    new_substitution = True

    # if fielding substitution, check if person is already in lineup
    if sub_type == 'fielding':
        if pid in lineup.player_id.values:
            new_substitution = False

    # check which spot in the lineup, get the playerID:
    sub_filter = (lineup.team_id == this_line['team_id']) & \
                 (lineup.bat_lineup == this_line['batting'])
    sub_index = lineup.index[sub_filter]

    # replace the person in the lineup
    lineup.at[sub_index[0], 'player_id'] = pid
    lineup.at[sub_index[0], 'player_nm'] = this_line['player_name']
    lineup.at[sub_index[0], 'fielding'] = field_pos

    return [lineup, sub_index, new_substitution]


# fielding stats collector
def field_collector(fid, lineup, the_line, stat_types):

    # get game info
    game_id = the_line['game_id']
    this_half = the_line['half_innings']
    actual_play = the_line['play']
    pitch_count = the_line['pitch_count']
    data_year = the_line['data_year']

    # get vis_team and home_team
    vis_team = lineup.loc[0, 'team_name']
    home_team = lineup.loc[10, 'team_name']

    # which team? find out in the_line -- THIS IS OPPOSITE to stat_collector!
    if the_line['team_id'] == '0':
        team_name = home_team  # home team is fielding
        stat_team = 'HOME'
    else:
        team_name = vis_team  # visiting team is fielding
        stat_team = 'VISIT'

    # gather more information about the play
    num_outs = the_line['outs']

    # base runners
    bases_taken = br.bases_occupied(the_line)

    # for each stat_type, call stat_appender
    for s_type in stat_types:
        sc.stat_appender(fid, team_name, data_year, game_id, this_half, s_type, 1, actual_play, pitch_count,
                         num_outs, bases_taken, stat_team, 'fielding')

    return True


# based on the fielding play, determine which stats should be recorded
def fielding_processor(begin_play, lineup, the_line):

    # look at the begin_play

    # starts with a number


    # starts with a letter


    return True
