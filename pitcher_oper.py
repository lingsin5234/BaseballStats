# libraries


# assign the pitcher
def assign_pitcher(lineup, this_line, is_sub):

    if is_sub:
        pitch_team = this_line['team_id']
    else:
        # check which team is batting
        if this_line['team_id'] == '0':
            pitch_team = '1'
        else:
            pitch_team = '0'

    # filter the corresponding pitcher_id
    pitch_filter = (lineup.team_id == pitch_team) & (lineup.fielding == '1')
    pitch_index = lineup.index[pitch_filter]
    pitcher_id = lineup.at[pitch_index[0], 'player_id']

    return pitcher_id, pitch_index[0]
