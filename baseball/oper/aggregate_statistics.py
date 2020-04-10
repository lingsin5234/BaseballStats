# this python file is for the job that aggregates all the STATS data by player_id, team_name and data_year
from . import database_reader as dr
from . import class_structure as cl
import pandas as pd


# aggregation function
def stats_aggregate(year):

    # start with batting stats
    query = "SELECT * FROM batting WHERE data_year=" + str(year)
    results = dr.baseball_db_reader(query)
    bat_col = [str(c).replace('batting.', '') for c in cl.batting_stats.columns]
    df = pd.DataFrame(results, columns=bat_col)

    # remove Id column and aggregate sum all columns, group by player_id, data_year, team_name
    agg_col = [c for c in bat_col if c not in ['Id', 'player_id', 'data_year', 'team_name']]
    # print(agg_col)
    # agg_sum = ["sum"] * len(agg_col)
    df = df.groupby(['player_id', 'data_year', 'team_name'])[agg_col].sum(axis=1)\
        .sort_values(by=['player_id', 'data_year', 'team_name']).reset_index()
    print(df[df['team_name'] == 'ATL'])

    # everyone selected for THIS year should be removed then add teh DF

    return True
