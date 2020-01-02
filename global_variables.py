# libraries
import pandas as pd

# create global tables.
player_stats = pd.DataFrame()

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

# global dictionary for stat types
bat_stats = {
    'GP': 'games_played',
    'GS': 'games_started',
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
    'SF': 'sac_fly'
    # 'PH': 'pinch_hit',
    # 'PR': 'pinch_run',
}

pitch_stats = {
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
    'BB': 'walks',
    'IBB': 'intentional_walks',
    'HBP': 'hit_batters',
    'POA': 'pick-off_attempts',
    'PO': 'pick-offs',
    'WP': 'wild_pitches',
    'PB': 'passed_balls',
    'BK': 'balks',
    'DI': 'defensive_indifference',
    'CI': 'catcher_interference'
}
