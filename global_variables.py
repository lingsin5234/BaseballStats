# libraries
import pandas as pd

# create global tables.
player = pd.DataFrame(columns=('player_id', 'game_id', 'stat_type', 'stat_value'))
game_roster = pd.DataFrame(columns=('game_id', 'which_team', 'player_id', 'fielding'))
player_stats = pd.DataFrame()