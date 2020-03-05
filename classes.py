# this file sets up the classes for the datasets and database
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

metadata = MetaData()

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
