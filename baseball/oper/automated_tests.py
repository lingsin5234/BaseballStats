# write the pujols and trea turner 2018 stat checks for automated testing
from . import db_setup as dbs
from . import global_variables as gv
import os, re
import pandas as pd
import numpy as np


# import pujols and turner 2018 stats
def import_test_cases():

    conn = dbs.engine.connect()
    conn.fast_executemany = True
    file_dir = 'baseball/import/tests'
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
                'data_year': 2018,
                'stat_category': stat_category
            }, index=[0])
            test_case.to_sql('test_cases', conn, if_exists='append', index=False)

            # get the test case Id
            query = 'SELECT Id FROM test_cases WHERE player_id=? AND data_year=? AND stat_category=?'
            results = conn.execute(query, player_id, 2018, stat_category).fetchall()
            print([r for (r,) in results])
            test_id = [r for (r,) in results]

            # write test data for specific test_id
            df['test_case'] = test_id[0]
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

    return True


import_test_cases()
