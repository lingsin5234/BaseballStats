# libraries
from . import global_variables as gv
from . import stat_collector as sc
from . import base_running as br
import re


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

    # keep the person subbed out on hand
    sub_out_id = lineup.at[sub_index[0], 'player_id']

    # replace the person in the lineup
    lineup.at[sub_index[0], 'player_id'] = pid
    lineup.at[sub_index[0], 'player_nm'] = this_line['player_name']
    lineup.at[sub_index[0], 'fielding'] = field_pos

    return [lineup, sub_index, new_substitution, sub_out_id]


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
def fielding_processor(field_index, lineup, the_line, stat_types):

    # check which team is batting
    if the_line['team_id'] == '0':
        field_team = '1'
    else:
        field_team = '0'

    # check which spot in the fielding, get the playerID:
    fld_filter = (lineup.team_id == field_team) & (lineup.fielding == str(field_index))
    fld_index = lineup.index[fld_filter]
    fid = lineup.at[fld_index[0], 'player_id']
    # print(field_index, fid, the_line)

    # send to field collector
    field_collector(fid, lineup, the_line, stat_types)

    return True


# get and send fielder position to record PO
def fielding_po(begin_play, grep_search, lineup, this_line):

    # remove (B) if not part of grep_search
    if not(bool(re.search(r'(B)', grep_search))):
        begin_play = re.sub(r'\(B\)', '', begin_play)

    # get the fielder position who made the putout
    try:
        fielders = fielding_unique(grep_search, begin_play)
    except Exception as e:
        print(grep_search, this_line['play'], begin_play, e)
    else:
        idx = len(fielders) - 1
        ft = ['PO']

        # send fielder position to processing (then collector)
        fielding_processor(fielders[idx], lineup, this_line, ft)

    return True


# return a unique list of fielding assists whilst keeping the order
# unique in reverse because the last fielder is key to put out in most cases
def fielding_unique(grep_search, begin_play):

    fielders = [int(f) for f in re.sub(grep_search, '', begin_play)]
    length = len(fielders)
    unique_set = set()
    for i in reversed(range(0, length)):
        if fielders[i] not in unique_set:
            unique_set.add(fielders[i])
        else:
            fielders.pop(i)

    return fielders


# common assigning assists and putouts/errors function
def fielding_assign_stats(grep_unique, the_play, lineup, this_line, ft1, ft2):

    fielders = fielding_unique(grep_unique, the_play)
    for idx in range(0, len(fielders)):
        if idx < len(fielders) - 1:
            # record the stat(s) for non-last fielders (usually this assigns 'A')
            fielding_processor(fielders[idx], lineup, this_line, ft1)
        else:
            # record stat(s) for last fielder (usually 'PO' or 'E')
            fielding_processor(fielders[idx], lineup, this_line, ft2)

    return True
