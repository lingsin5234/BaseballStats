# write the pujols and trea turner 2018 stat checks for automated testing
from . import db_setup as dbs
from . import global_variables as gv
from . import date_time as dt
import os, re
import pandas as pd
import numpy as np
import time as t
import json


# import pujols and turner 2018 stats
def import_test_cases(yr):

    conn = dbs.engine.connect()
    conn.fast_executemany = True
    file_dir = 'baseball/import/tests/' + str(yr)
    try:
        files = os.listdir(file_dir)
        for f in files:
            df = pd.read_csv(os.path.join(file_dir, f))
            stat_category = re.sub(r'\.csv', '', re.sub(r'.*/', '', f))
            player_id = re.sub(r'.*_', '', stat_category)
            stat_category = re.sub(r'_.*', '', stat_category)
            if stat_category == 'batting':
                df = df.rename(columns={'2B': 'D', '3B': 'T'})  # cannot start with number
            print(player_id, stat_category)
            # write test case
            test_case = pd.DataFrame({
                'player_id': player_id,
                'data_year': yr,
                'stat_category': stat_category
            }, index=[0])
            test_case.to_sql('test_cases', conn, if_exists='append', index=False)

            # get the test case Id
            query = 'SELECT Id FROM test_cases WHERE player_id=? AND data_year=? AND stat_category=?'
            results = conn.execute(query, player_id, yr, stat_category).fetchall()
            print([r for (r,) in results])
            test_id = [r for (r,) in results]

            # write test data for specific test_id
            df['test_case'] = test_id[0]
            df = df.fillna(0)
            db_name = 'test_' + stat_category
            df.to_sql(db_name, conn, if_exists='append', index=False)
    except Exception as e:
        print('Import Tests Failed:', e)

    # read from database
    query = 'SELECT * FROM test_batting'
    results = conn.execute(query).fetchall()
    batting = {}
    idx = 0
    for x in results:
        batting[idx] = dict(x)
        idx += 1
    print(pd.DataFrame.from_dict(batting).transpose())

    query = 'SELECT * FROM test_fielding'
    results = conn.execute(query).fetchall()
    fielding = {}
    idx = 0
    for x in results:
        fielding[idx] = dict(x)
        idx += 1
    print(pd.DataFrame.from_dict(fielding).transpose())
    conn.close()

    return True


# import_test_cases()


# run test cases
def run_test_cases(stat_category, yr):

    # connect to database
    conn = dbs.engine.connect()
    conn.fast_executemany = True
    db_name = 'test_' + stat_category

    # get test cases
    query = 'SELECT ts.*, tc.player_id, tc.data_year FROM ' + db_name + ' ts JOIN test_cases tc ' + \
            'ON ts.test_case = tc.Id WHERE tc.data_year=?'
    a = t.time()
    results = conn.execute(query, yr).fetchall()
    # print('Fetch All:', dt.seconds_convert(t.time() - a))
    b = t.time()
    columns = conn.execute(query, yr)
    # print('Columns:', dt.seconds_convert(t.time() - b))
    # print(columns.keys())
    tc = pd.DataFrame(results)
    tc.columns = columns.keys()
    # print(tc)

    # get category results
    player_id = tc['player_id'].unique().tolist()
    data_year = tc['data_year'].unique().tolist()
    print(player_id, type(data_year[0]), type(2018))
    for pid in player_id:
        query = 'SELECT * FROM raw_player_stats WHERE player_id=? AND bat_pitch=? AND data_year=?'
        results = conn.execute(query, pid, stat_category, data_year[0]).fetchall()
        columns = conn.execute(query, pid, stat_category, data_year[0])
        stats = pd.DataFrame(results)
        stats.columns = columns.keys()
        # print(stats)

        # tally by date
        stats['GameDate'] = stats['game_id'].replace(r'^[A-Z]{3}([0-9]{4})([0-9]{2})([0-9]{2})(.*)',
                                                     '\\1-\\2-\\3(\\4)', regex=True)
        stats['GameDate'] = stats['GameDate'].replace(r'\(0\)', '', regex=True)  # for double headers
        agg_stats = stats[['GameDate', 'stat_type', 'stat_value']].groupby(['GameDate', 'stat_type'])\
            .agg({'stat_value': 'sum'}).reset_index()
        agg_stats = agg_stats.set_index(['GameDate']).pivot(columns='stat_type')['stat_value']
        agg_stats = agg_stats.fillna(0)
        # print(agg_stats)
        # print(len(agg_stats), len(tc[tc['player_id'] == pid]))

        # compare with test case
        print(compare_data(agg_stats, tc[tc['player_id'] == pid].set_index(['GameDate'])))

    # df = df.rename(columns=gv.bat_stat_types)

    return True


# compare columns for data frames
def compare_data(df1, df2):

    # first check if lengths are the same
    # print(len(df1), len(df2))
    if len(df1) != len(df2):
        return {'Status': 'Failed. DataFrame Lengths Different', 'columns': ''}

    # get comparable columns
    col1 = df1.columns.tolist()
    col2 = df2.columns.tolist()
    # ignores index: GameDate
    col_comp = set(col1) & set(col2)
    # print(col_comp)

    # compare the columns
    fail_flag = False
    failed = []
    for c in col_comp:
        df1[c] = df1[c].apply(int)
        comp_bool = df1[c].where(df1[c] == df2[c]).notna()
        if comp_bool.all():
            # success!
            pass
        else:
            # print(c, '\n', comp_bool)
            idx = comp_bool[comp_bool == False].index
            df_comp = pd.concat([df1.loc[idx, c], df2.loc[idx, c]], axis=1)
            df_comp.columns = ['raw_' + c, 'test_case_' + c]
            fail_flag = True
            print(df_comp)

    if not fail_flag:
        results = {'Status': 'Success', 'columns': '100% match'}
    else:
        results = {'Status': 'Failed. Column Mismatches', 'columns': failed}

    # write to log
    fgp = open('TEST_CASES.LOG', mode='a')
    fgp.write('Automated Testing: ' + json.dumps(results, indent=4))
    fgp.close()

    return results


# run_test_cases('batting')
