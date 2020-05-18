# this python file is for the job that aggregates all the STATS data by player_id, team_name and data_year
from . import database_reader as dr
from . import class_structure as cl
from . import db_setup as dbs
import pandas as pd


# aggregation function
def stats_aggregate(year):

    # connect to database
    conn = dbs.engine.connect()
    conn.fast_executemany = True

    # handle both batting and pitching
    stat_types = ['batting', 'pitching']
    stat_colums = {'batting': cl.batting_stats.columns, 'pitching': cl.pitching_stats.columns}

    for stat in stat_types:

        # start with batting stats
        query = "SELECT * FROM " + stat + " WHERE data_year=" + str(year)
        results = dr.baseball_db_reader(query)
        stat_col = [str(c).replace(stat + '.', '') for c in stat_colums[stat]]
        df = pd.DataFrame(results, columns=stat_col)
        print("Length of Database: ", len(df))

        # remove Id column and aggregate sum all columns, group by player_id, data_year, team_name
        agg_col = [c for c in stat_col if c not in ['Id', 'player_id', 'data_year', 'team_name']]
        # print(agg_col)
        # agg_sum = ["sum"] * len(agg_col)
        agg_df = df.groupby(['player_id', 'data_year', 'team_name'])[agg_col].sum(axis=1)\
            .sort_values(by=['player_id', 'data_year', 'team_name']).reset_index()
        # print(agg_df[agg_df['team_name'] == 'ATL'])
        print("Length of Agg_df: ", len(agg_df))

        # everyone selected for THIS year should be removed then add the DF
        query = "DELETE FROM " + stat + " WHERE Id in ("
        remove_ids = df['Id']
        query = query + ','.join(map(str, remove_ids)) + ")"
        # print(query)
        results = dr.baseball_db_remove(query)
        print("Removal of", stat, ":", results)

        # now insert the table
        agg_df.to_sql(stat, conn, if_exists='append', index=False)

    conn.close()
    return True
