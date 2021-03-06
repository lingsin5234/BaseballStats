# this file sets up the classes for the datasets and database
from sqlalchemy import Table, Column, Integer, String, Float, MetaData, ForeignKey, UniqueConstraint

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
                  Column('stat_category', String),
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


# teams table
teams = Table('teams', metadata,
              Column('Id', Integer, primary_key=True),
              Column('data_year', Integer),
              Column('team_id', String),
              Column('league_id', String),
              Column('city_name', String),
              Column('name_of_team', String),
              Column('team_name', String),
              UniqueConstraint('data_year', 'team_id', name='teams_tbl'))


# players table
players = Table('players', metadata,
                Column('Id', Integer, primary_key=True),
                Column('data_year', Integer),
                Column('player_id', String),
                Column('last_name', String),
                Column('first_name', String),
                Column('bats', String),
                Column('throws', String),
                Column('team_id', String),
                Column('position', String),
                UniqueConstraint('data_year', 'player_id', 'team_id', name='players_tbl'))


# starters table
starters = Table('starters', metadata,
                 Column('Id', Integer, primary_key=True),
                 Column('data_year', Integer),
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
                 Column('data_year', Integer),
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
                         Column('data_year', Integer),
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
                         Column('bat_pitch', String),
                         UniqueConstraint('Id', name='raw_player_stats_Id'))

# player_year_team table
player_year_team = Table('player_year_team', metadata,
                         Column('Id', Integer, primary_key=True),
                         Column('player_id', String),
                         Column('data_year', Integer),
                         Column('team_name', String),
                         Column('stat_category', String),
                         Column('date_generated', String),
                         UniqueConstraint('player_id', 'data_year', 'team_name', 'stat_category', name='PYTS'))

# batting stats table
batting_stats = Table('batting', metadata,
                      Column('Id', Integer, primary_key=True),
                      Column('pyts_id', ForeignKey('player_year_team.Id')),
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
                      Column('ground_dp', Integer),
                      Column('hit_by_pitch', Integer),
                      Column('sac_hit', Integer),
                      Column('sac_fly', Integer),
                      Column('pinch_hit', Integer),
                      Column('pinch_run', Integer),
                      UniqueConstraint('pyts_id', name='batting_stats'))

# pitching stats table
pitching_stats = Table('pitching', metadata,
                       Column('Id', Integer, primary_key=True),
                       Column('pyts_id', ForeignKey('player_year_team.Id')),
                       Column('games_played', Integer),
                       Column('games_started', Integer),
                       Column('innings_pitched', Integer),
                       Column('batters_faced', Integer),
                       Column('wins', Integer),
                       Column('losses', Integer),
                       Column('holds', Integer),
                       Column('saves', Integer),
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
                       Column('foul_balls', Integer),
                       UniqueConstraint('pyts_id', name='pitching_stats'))

# fielding stats table
fielding = Table('fielding', metadata,
                 Column('Id', Integer, primary_key=True),
                 Column('pyts_id', ForeignKey('player_year_team.Id')),
                 Column('games_played', Integer),
                 Column('games_started', Integer),
                 Column('innings_played', Float),
                 # Column('batters_faced', Integer),
                 # Column('wins', Integer),
                 # Column('losses', Integer),
                 # Column('holds', Integer),
                 # Column('saves', Integer),
                 # Column('runs_allowed', Integer),
                 # Column('earned_runs', Integer),
                 Column('assists', Integer),
                 Column('put_outs', Integer),
                 Column('double_plays', Integer),
                 Column('triple_plays', Integer),
                 Column('errors', Integer),
                 UniqueConstraint('pyts_id', name='fielding_stats'))

# batting calculated stats table
batting_calc = Table('batting_calc', metadata,
                     Column('Id', Integer, primary_key=True),
                     Column('pyts_id', ForeignKey('player_year_team.Id')),
                     Column('singles', Integer),
                     Column('total_bases', Integer),
                     Column('total_outs', Integer),
                     Column('batting_avg', Float),
                     Column('slugging', Float),
                     Column('on_base_per', Float),
                     Column('obp_slug', Float),
                     Column('obp_slug_plus', Float),
                     Column('batting_avg_bip', Float),
                     Column('on_base', Integer),
                     Column('bases_adv', Float),
                     Column('opportunities', Integer),
                     Column('runs_created', Float),
                     Column('runs_created_per', Float),
                     UniqueConstraint('pyts_id', name='batting_calc'))

# test case stats
test_cases = Table('test_cases', metadata,
                   Column('Id', Integer, primary_key=True),
                   Column('player_id', String),
                   Column('data_year', Integer),
                   Column('stat_category', String),
                   UniqueConstraint('player_id', 'data_year', 'stat_category', name='player_year_stat'))

test_batting = Table('test_batting', metadata,
                     Column('Id', Integer, primary_key=True),
                     Column('test_case', ForeignKey('test_cases.Id')),
                     Column('GameDate', String),
                     Column('PA', Integer),
                     Column('AB', Integer),
                     Column('R', Integer),
                     Column('H', Integer),
                     Column('D', Integer),
                     Column('T', Integer),
                     Column('HR', Integer),
                     Column('RBI', Integer),
                     Column('BB', Integer),
                     Column('IBB', Integer),
                     Column('SO', Integer),
                     Column('HBP', Integer),
                     Column('SH', Integer),
                     Column('SF', Integer),
                     Column('ROE', Integer),
                     Column('GDP', Integer),
                     Column('SB', Integer),
                     Column('CS', Integer),
                     Column('BA', Float),
                     Column('OBP', Float),
                     Column('SLG', Float),
                     Column('OPS', Float),
                     Column('BOP', Integer),
                     Column('aLI', Float),
                     Column('WPA', Float),
                     Column('RE24', Float),
                     Column('DFS_DK', Float),
                     Column('DFS_FD', Float),
                     Column('Pos', String))

test_fielding = Table('test_fielding', metadata,
                      Column('Id', Integer, primary_key=True),
                      Column('test_case', ForeignKey('test_cases.Id')),
                      Column('GameDate', String),
                      Column('BF', Integer),
                      Column('Inn', Float),
                      Column('PO', Integer),
                      Column('A', Integer),
                      Column('E', Integer),
                      Column('Ch', Integer),
                      Column('DP', Integer),
                      Column('Pos', String))
