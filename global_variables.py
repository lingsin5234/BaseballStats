# libraries
import pandas as pd

# create global tables.
player = pd.DataFrame(columns=('player_id', 'game_id', 'this_half', 'stat_type', 'stat_value', 'actual_play'))
game_roster = pd.DataFrame(columns=('game_id', 'which_team', 'player_id', 'fielding'))
player_stats = pd.DataFrame()

# global dictionary for stat types
bat_stats = {
    'AB': 'at_bat',
    'PA': 'plate_app',
    'H': 'hits',
    'D': 'doubles',
    'T': 'triples',
    'HR': 'home_run',
    'RBI': 'rbi',
    'R': 'runs_scored',
    'BB': 'walks',
    'IW': 'int_walks',
    'SB': 'stolen_base',
    'CS': 'caught_stealing',
    'LOB': 'left_on_base',
    'RLSP': 'rlsp',
    'HBP': 'hit_by_pitch',
    'SH': 'sac_hit',
    'SF': 'sac_fly',
    'GP': 'games_played',
    'GS': 'games_started',
    'PH': 'pinch_hit',
    'PR': 'pinch_run'
}
