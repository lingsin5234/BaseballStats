# this script runs the batting stats thru calculations to produce
# the calculated stats, e.g. BAA
from . import db_setup as dbs
from . import date_time as dt
from . import error_logger as el
import pandas as pd
import time as t


def calculate_bat_stats(results, columns, year):

    t1_time = t.time()
    # convert batting to data frame
    batting = pd.DataFrame(results)
    batting.columns = columns.keys()
    # print(batting.head())
    # print(len(batting['pyts_id'].unique()), len(batting))

    # calculate league sums (ls)
    ls = batting.agg(['sum'])

    # league calculations
    ls['on_base_per'] = (ls['hits'] + ls['walks'] + ls['hit_by_pitch']) / \
                        (ls['at_bats'] + ls['walks'] + ls['hit_by_pitch'] + ls['sac_fly'])
    ls['singles'] = ls['hits'] - ls['doubles'] - ls['triples'] - ls['home_runs']
    ls['total_bases'] = ls['singles'] + ls['doubles']*2 + ls['triples']*3 + ls['home_runs']*4
    ls['slugging'] = ls['total_bases'] / ls['at_bats']
    league_on_base_per = ls['on_base_per']['sum']  # THIS NEEDS TO EXCLUDE PITCHERS!!!
    league_slugging = ls['slugging']['sum']
    # print(ls)
    # print(ls.columns)

    # player stats calculations
    pyts_ids = batting['pyts_id'].unique().tolist()
    all_calc_stats = []
    for pid in pyts_ids:
        b = batting.loc[batting['pyts_id'] == pid].copy()
        b = b.to_dict(orient='records')[0]
        p = dict()
        p['pyts_id'] = pid

        p['singles'] = b['hits'] - b['doubles'] - b['triples'] - b['home_runs']
        p['total_bases'] = p['singles'] + b['doubles'] * 2 + b['triples'] * 3 + b['home_runs'] * 4
        p['total_outs'] = (b['at_bats'] - b['hits']) + b['ground_dp'] + b['sac_fly'] \
                          + b['sac_hit'] + b['caught_stealing']

        if b['at_bats'] == 0:
            # print(b['hits'], b['at_bats'])
            p['batting_avg'] = 0
            p['slugging'] = 0
        else:
            p['batting_avg'] = b['hits'] / b['at_bats']
            p['slugging'] = p['total_bases'] / b['at_bats']

        if (b['at_bats'] + b['walks'] + b['hit_by_pitch'] + b['sac_fly']) == 0:
            p['on_base_per'] = 0
        else:
            p['on_base_per'] = (b['hits'] + b['walks'] + b['hit_by_pitch']) / \
                               (b['at_bats'] + b['walks'] + b['hit_by_pitch'] + b['sac_fly'])

        p['obp_slug'] = p['on_base_per'] + p['slugging']
        p['obp_slug_plus'] = 100 * ((p['on_base_per'] / league_on_base_per) + (p['slugging'] / league_slugging) - 1)
        if (b['at_bats'] - b['strikeouts'] - b['home_runs'] + b['sac_fly']) == 0:
            # print(b['at_bats'], b['strikeouts'],  b['home_runs'], b['sac_fly'])
            p['batting_avg_bip'] = 0
        else:
            p['batting_avg_bip'] = (b['hits'] - b['home_runs']) / \
                                   (b['at_bats'] - b['strikeouts'] - b['home_runs'] + b['sac_fly'])

        p['on_base'] = b['hits'] + b['walks'] + b['hit_by_pitch'] - b['caught_stealing'] - b['ground_dp']
        p['bases_adv'] = p['total_bases'] + .26 * (b['walks'] + b['hit_by_pitch'] - b['intentional_walks']) + \
                         .52 * (b['sac_hit'] + b['sac_fly'] + b['stolen_bases'])

        p['opportunities'] = b['at_bats'] + b['walks'] + b['hit_by_pitch'] + b['sac_hit'] + b['sac_fly']

        if p['opportunities'] == 0:
            p['runs_created'] = 0
        else:
            p['runs_created'] = p['on_base'] * p['bases_adv'] / p['opportunities']

        if p['total_outs'] == 0:
            p['runs_created_per'] = 0
        else:
            p['runs_created_per'] = p['runs_created'] / (p['total_outs'] / 27)
        all_calc_stats.append(p)

    # convert to data frame, then submit to database
    df = pd.DataFrame(all_calc_stats)
    # print(df)

    try:
        # write the STATS to corresponding database
        conn = dbs.engine.connect()
        conn.fast_executemany = True
        update_time = t.time()
        df.to_sql('batting_calc', conn, if_exists='append', index=False)
        print('Upload Batting Calculated Stats to Database: ', dt.seconds_convert(t.time() - update_time))
        conn.close()
    except Exception as e:
        # accept any type of errors
        el.error_logger(e, 'WRITE batting calculated stats: ' + str(e), 'ALL', year, 'batting')
        return False

    try:
        # WRITING STATS PERFORMANCE
        t2_time = t.time()
        fgp = open('GAMEPLAY.LOG', mode='a')
        fgp.write('Calculated Stats Processing: ' + str(dt.seconds_convert(t2_time - t1_time)) + '\n')
        print('Calculated Stats Processing: ', dt.seconds_convert(t2_time - t1_time))
        fgp.close()
    except Exception as e:
        # accept any types of errors
        el.error_logger(e, 'WRITE batting calculated stats performance: ' + str(e), 'ALL', year, 'batting')
        return False

    return True
