# libraries
import global_variables as gv


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
    lineup.at[sub_index[0], 'player_nm'] = this_line['name']
    lineup.at[sub_index[0], 'fielding'] = field_pos

    return [lineup, sub_index, new_substitution]
