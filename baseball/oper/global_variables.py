# libraries
import pandas as pd

# import directory
is_prod = True
if is_prod:
    data_dir = 'baseball/import'
else:
    data_dir = 'import'

# create global tables.
player_stats = pd.DataFrame()

# pujols tracker -- just to help check fielding lol
pujols_tracker = {
    'A': 0,
    'PO': 0,
    'E': 0,
    'DP': 0,
    'TP': 0,
    'game_id': '',
    'this_half': '',
    'play': '',
    'stat_type': '',
    'batter': ''
}

# create dictionary for storing player data to be processed later
# with an unknown number of entries - index stored in player_idx
player = {}
player_idx = 0

# create another dictionary for storing temp EVENT output data
full_output = {}
fo_idx = 0

# dictionary for game roster
game_roster = {}
gr_idx = 0

# for tracking baserunners
bases_after = '---'

# debugging pyts
pyts_debug = []

# global dictionary for stat types
bat_stat_types = {
    'PID': 'player_id',
    'YEAR': 'data_year',
    'TEAM': 'team_name',
    'GP': 'games_played',
    'GS': 'games_started',
    'AB': 'at_bats',
    'PA': 'plate_appearances',
    'H': 'hits',
    'D': 'doubles',
    'T': 'triples',
    'HR': 'home_runs',
    'RBI': 'rbis',
    'R': 'runs_scored',
    'BB': 'walks',
    'IW': 'intentional_walks',
    'K': 'strikeouts',
    'SB': 'stolen_bases',
    'CS': 'caught_stealing',
    'LOB': 'left_on_base',
    'RLSP': 'rlsp',
    'GDP': 'ground_dp',
    'HBP': 'hit_by_pitch',
    'SH': 'sac_hit',
    'SF': 'sac_fly',
    'PH': 'pinch_hit',
    'PR': 'pinch_run',
}

pitch_stat_types = {
    'PID': 'player_id',
    'YEAR': 'data_year',
    'TEAM': 'team_name',
    'GP': 'games_played',
    'GS': 'games_started',
    'IP': 'innings_pitched',
    'BF': 'batters_faced',
    # 'W': 'wins',
    # 'L': 'losses',
    # 'HD': 'holds',
    # 'SV': 'saves',
    'R': 'runs_allowed',
    'ER': 'earned_runs',
    'H': 'hits_allowed',
    'HR': 'home_runs',
    'K': 'strikeouts',
    'BB': 'walks',
    'IBB': 'intentional_walks',
    'HBP': 'hit_batters',
    'POA': 'pick_off_attempts',
    'PO': 'pick_offs',
    'WP': 'wild_pitches',
    'PB': 'passed_balls',
    'BK': 'balks',
    'DI': 'defensive_indifference',
    'CI': 'catcher_interference',
    'PT': 'pitches_thrown',
    'ST': 'strikes_thrown',
    'BT': 'balls_thrown',
    'FL': 'foul_balls'
}

field_stat_types = {
    'PID': 'player_id',
    'YEAR': 'data_year',
    'TEAM': 'team_name',
    'GP': 'games_played',
    'GS': 'games_started',
    'IP': 'innings_played',
    # 'BF': 'batters_faced',
    # 'W': 'wins',
    # 'L': 'losses',
    # 'HD': 'holds',
    # 'SV': 'saves',
    # 'R': 'runs_allowed',
    # 'ER': 'earned_runs',
    'A': 'assists',
    'PO': 'put_outs',
    'DP': 'double_plays',
    'TP': 'triple_plays',
    'E': 'errors'
}

bat_calc_stat_types = {
    ''
}

