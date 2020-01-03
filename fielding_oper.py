# libraries
import global_variables as gv


# fielding substitutions
def lineup_substitution(this_line, lineup, pid, sub_type):

    # by default, all substitutions are new except when handling Fielding Subs
    new_substitution = True

    # if fielding substitution, check if person is already in lineup
    if sub_type == 'fielding':
        if pid in lineup.player_id:
            new_substitution = False
            print(this_line)
            print(lineup)
            exit()

    # check which spot in the lineup, get the playerID:
    if sub_type == 'batting':
        sub_filter = (lineup.team_id == this_line['team_id']) & \
                     (lineup.bat_lineup == this_line[sub_type])
        sub_index = lineup.index[sub_filter]
    elif sub_type == 'fielding':
        sub_filter = (lineup.team_id == this_line['team_id']) & \
                     (lineup.fielding == this_line[sub_type])
        sub_index = lineup.index[sub_filter]
    else:
        print('Substitution Error: Fielding Oper')
        exit()

    # replace the person in the lineup
    lineup.at[sub_index[0], 'player_id'] = pid
    lineup.at[sub_index[0], 'player_nm'] = this_line['name']

    return [lineup, sub_index, new_substitution]
