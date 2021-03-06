# this script processes the statistics from the processed imports
import time as t
import sys
from . import global_variables as gv
from . import stat_collector as sc
from . import date_time as dt
from . import db_setup as dbs
from . import error_logger as el
from . import check_latest_imports as chk
import pandas as pd
import datetime
from sqlalchemy.exc import IntegrityError


# splitting the generate_stats function into separate jobs => separate functions
def generate_stats2(year, team, stat_category):

    t1_time = t.time()

    try:
        # retrieve the game player stats
        conn = dbs.engine.connect()
        conv_time = t.time()

        # put fetched raw player stats and form player dictionaries
        idx = 0
        output = conn.execute("SELECT * FROM raw_player_stats WHERE data_year=? AND bat_pitch=? AND team_name=?",
                              year, stat_category, team).fetchall()
        for x in output:
            gv.player[idx] = dict(x)
            idx += 1
        print('Conversion Time:', dt.seconds_convert(t.time() - conv_time))
    except Exception as e:
        # accept any types of errors
        el.error_logger(e, 'Query & Convert Raw Player Stats: ' + str(e), team, year, stat_category)
        return False

    try:
        gv.player_stats = sc.stat_organizer2(gv.player, stat_category)
        # t.sleep(10)
    except Exception as e:
        # accept any types of errors
        el.error_logger(e, 'STAT_ORGANIZER: ' + str(e), team, year, stat_category)
        return False

    try:
        # reassign column names
        gen_stats = gv.player_stats[stat_category]
        if stat_category == 'batting':
            gen_stats = gen_stats.rename(columns=gv.bat_stat_types)
        elif stat_category == 'pitching':
            gen_stats = gen_stats.rename(columns=gv.pitch_stat_types)
        elif stat_category == 'fielding':
            gen_stats = gen_stats.rename(columns=gv.field_stat_types)
    except Exception as e:
        # accept any types of errors
        el.error_logger(e, 'Re-assign Columns: ' + str(e), team, year, stat_category)
        return False

    try:
        # check player_year_team table to get/create pyts_id, then remove player, year, team
        check_time = t.time()
        conn.fast_executemany = True
        gen_stats = check_pyts(gen_stats, conn, year, stat_category)
        gen_stats = gen_stats.drop(columns=['player_id', 'data_year', 'team_name'])
        print('CHECK PYTS Table:', dt.seconds_convert(t.time() - check_time))
    except Exception as e:
        # accept any type of errors
        el.error_logger(e, 'Check PYTS table: ' + str(e), team, year, stat_category)
        return False

    # DEBUGGING: print repeat?
    query = 'SELECT pyts_id FROM ' + stat_category
    db_pyts = conn.execute(query).fetchall()
    db_pyts = [n for (n,) in db_pyts]
    gen_pyts = gen_stats.loc[gen_stats['pyts_id'].isin(db_pyts), 'pyts_id']

    try:
        # write the STATS to corresponding database
        update_time = t.time()
        gen_stats.to_sql(stat_category, conn, if_exists='append', index=False)
        print('Import', stat_category.upper(), 'STATS to Database: ', dt.seconds_convert(t.time() - update_time))
    except IntegrityError as e:
        el.error_logger(e, 'UNIQUE constraint: ' + str(e), team, year, stat_category)
        print("ALREADY IN DB:", gen_pyts)
        t.sleep(5)
        # keep going
    except Exception as e:
        # accept any other type of errors
        el.error_logger(e, 'WRITE stats: ' + str(e), team, year, stat_category)
        return False

    try:
        # WRITING STATS PERFORMANCE
        t2_time = t.time()
        fgp = open('GAMEPLAY.LOG', mode='a')
        fgp.write('Stats Processing: ' + str(dt.seconds_convert(t2_time - t1_time)) + '\n')
        print('Stats Processing: ', dt.seconds_convert(t2_time - t1_time))
        fgp.close()
    except Exception as e:
        # accept any types of errors
        el.error_logger(e, 'WRITE stats performance: ' + str(e), team, year, stat_category)
        return False

    # send completion notice
    finish_str = {
        'process_name': 'stat_processor: ' + stat_category,
        'data_year': year,
        'team_name': team,
        'time_elapsed': t2_time - t1_time,
        'timestamp': t.strftime("%Y-%m-%d %H:%M:%S", t.localtime())
    }
    completion = pd.DataFrame([finish_str])
    completion.to_sql('process_log', conn, if_exists='append', index=False)
    # conn.close()

    return True


# function that checks for player_ids already existing in the player_year_team table
# if it does not exist, then adds the corresponding ones
def check_pyts(gen_stats, conn, data_year, stat_category):

    gen_stats['pyts_id'] = 0
    df_unique = gen_stats[['player_id', 'team_name']].drop_duplicates()
    # print(df_unique)
    for index, row in df_unique.iterrows():
        query = 'SELECT Id FROM player_year_team WHERE player_id=? AND data_year=? AND team_name=? AND stat_category=?'
        results = conn.execute(query, row['player_id'], data_year, row['team_name'], stat_category).fetchall()

        # add new entry if no results
        if len(results) == 0:
            entry = {
                'player_id': row['player_id'],
                'data_year': data_year,
                'team_name': row['team_name'],
                'stat_category': stat_category,
                'date_generated': str(datetime.datetime.now())
            }
            pd.DataFrame([entry]).to_sql('player_year_team', conn, if_exists='append', index=False)

            # retrieve entry
            results = conn.execute(query, row['player_id'], data_year, row['team_name'], stat_category).fetchall()

        results = [n for (n,) in results]
        # print(results[0])
        gen_stats.loc[(gen_stats['player_id'] == row['player_id']) & (gen_stats['team_name'] == row['team_name']),
                      'pyts_id'] = results[0]

    return gen_stats
