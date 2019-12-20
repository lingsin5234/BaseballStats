# libraries
import pandas as pd

# create global tables.
game_roster = pd.DataFrame(columns=('game_id', 'player_id', 'player_nm', 'team', 'bat_lineup', 'fielding'))
player_stats = pd.DataFrame()

# create dictionary for storing player data to be processed later
# with an unknown number of entries - index stored in player_idx
player = {}
player_idx = 0

# create another dictionary for storing temp EVENT output data
full_output = {}
fo_idx = 0

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
