# this file sets up the classes for the datasets and database
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

metadata = MetaData()

# process log table
process_log = Table('process_log', metadata,
                    Column('Id', Integer, primary_key=True),
                    Column('process_name', String),
                    Column('data_year', Integer),
                    Column('team_name', String, nullable=True),
                    Column('time_elapsed', String),
                    Column('timestamp', String))

# error log table
error_log = Table('error_log', metadata,
                  Column('Id', Integer, primary_key=True),
                  Column('process_name', String),
                  Column('data_year', Integer),
                  Column('team_name', String),
                  Column('error', String),
                  Column('timestamp', String))

# processing_errors table
processing_errors = Table('processing_errors', metadata,
                          Column('Id', Integer, primary_key=True),
                          Column('process_name', String),
                          Column('data_year', Integer),
                          Column('team_name', String),
                          Column('game_id', String),
                          Column('half_inning', String),
                          Column('error', String),
                          Column('timestamp', String))

# starters table
starters = Table('starters', metadata,
                 Column('Id', Integer, primary_key=True),
                 Column('game_id', String),
                 Column('player_id', String),
                 Column('player_nm', String),
                 Column('team_id', Integer),
                 Column('team_name', String),
                 Column('bat_lineup', Integer),
                 Column('fielding', Integer))

# gameplay table
gameplay = Table('gameplay', metadata,
                 Column('Id', Integer, primary_key=True),
                 Column('game_id', String),
                 Column('gm_type', String),
                 Column('inning', Integer),
                 Column('half', Integer),
                 Column('half_innings', String),
                 Column('playerID', String),
                 Column('pitch_count', String),
                 Column('pitches', String),
                 Column('play', String),
                 Column('player_name', String),
                 Column('team_id', String),
                 Column('team_name', String),
                 Column('batting', Integer),
                 Column('fielding', Integer),
                 Column('pitcherID', String),
                 Column('outs', Integer),
                 Column('before_1B', String),
                 Column('before_2B', String),
                 Column('before_3B', String),
                 Column('after_1B', String),
                 Column('after_2B', String),
                 Column('after_3B', String),
                 Column('runs_scored', Integer),
                 Column('total_scored', Integer))

# raw player stats table
raw_player_stats = Table('raw_player_stats', metadata,
                         Column('Id', Integer, primary_key=True),
                         Column('player_id', String),
                         Column('team_name', String),
                         Column('game_id', String),
                         Column('this_half', Integer),
                         Column('stat_type', String),
                         Column('stat_value', Integer),
                         Column('actual_play', String),
                         Column('pitch_count', String),
                         Column('num_outs', Integer),
                         Column('bases_taken', String),
                         Column('stat_team', Integer),
                         Column('bat_pitch', String))

# batting stats table
batting_stats = Table('batting', metadata,
                      Column('Id', Integer, primary_key=True),
                      Column('player_id', String),
                      Column('team_name', String),
                      Column('games_played', Integer),
                      Column('games_started', Integer),
                      Column('at_bats', Integer),
                      Column('plate_appearances', Integer),
                      Column('hits', Integer),
                      Column('doubles', Integer),
                      Column('triples', Integer),
                      Column('home_runs', Integer),
                      Column('rbis', Integer),
                      Column('runs_scored', Integer),
                      Column('walks', Integer),
                      Column('intentional_walks', Integer),
                      Column('strikeouts', Integer),
                      Column('stolen_bases', Integer),
                      Column('caught_stealing', Integer),
                      Column('left_on_base', Integer),
                      Column('rlsp', Integer),
                      Column('hit_by_pitch', Integer),
                      Column('sac_hit', Integer),
                      Column('sac_fly', Integer)
                      # , Column('pinch_hit', Integer),
                      # Column('pinch_run', Integer)
                      )

# pitching stats table
pitching_stats = Table('pitching', metadata,
                       Column('Id', Integer, primary_key=True),
                       Column('player_id', String),
                       Column('team_name', String),
                       Column('games_played', Integer),
                       Column('games_started', Integer),
                       Column('innings_pitched', Integer),
                       Column('batters_faced', Integer),
                       # Column('wins', Integer),
                       # Column('losses', Integer),
                       # Column('holds', Integer),
                       # Column('saves', Integer),
                       Column('runs_allowed', Integer),
                       Column('earned_runs', Integer),
                       Column('hits_allowed', Integer),
                       Column('home_runs', Integer),
                       Column('strikeouts', Integer),
                       Column('walks', Integer),
                       Column('intentional_walks', Integer),
                       Column('hit_batters', Integer),
                       Column('pick_off_attempts', Integer),
                       Column('pick_offs', Integer),
                       Column('wild_pitches', Integer),
                       Column('passed_balls', Integer),
                       Column('balks', Integer),
                       Column('defensive_indifference', Integer),
                       Column('catcher_interference', Integer),
                       Column('pitches_thrown', Integer),
                       Column('strikes_thrown', Integer),
                       Column('balls_thrown', Integer),
                       Column('foul_balls', Integer))
