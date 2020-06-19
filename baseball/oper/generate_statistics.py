# this script processes the statistics from the processed imports
import time as t
import sys
from . import global_variables as gv
from . import stat_collector as sc
from . import date_time as dt
from . import db_setup as dbs
from . import error_logger as el
import pandas as pd


'''
def generate_stats(year, team):

    t1_time = t.time()

    try:
        # retrieve the game player stats
        conn = dbs.engine.connect()
        output = conn.execute("SELECT * FROM raw_player_stats WHERE team_name=? AND data_year=?",
                              team, year).fetchall()
        idx = 0
        # conversion time
        conv_time = t.time()
        for x in output:
            gv.player[idx] = dict(x)
            idx += 1
        print('Conversion Time:', dt.seconds_convert(t.time() - conv_time))
    except Exception as e:
        # accept any types of errors
        el.error_logger(e, 'Query & Convert Raw Player Stats: ' + str(e), team, year)
        return False

    try:
        gv.player_stats = sc.stat_organizer(gv.player)
    except Exception as e:
        # accept any types of errors
        el.error_logger(e, 'STAT_ORGANIZER: ' + str(e), team, year)
        return False

    try:
        # separate batting and pitching stats, reassign column names
        bat_stats = gv.player_stats['batting']
        pitch_stats = gv.player_stats['pitching']
        bat_stats = bat_stats.rename(columns=gv.bat_stat_types)
        pitch_stats = pitch_stats.rename(columns=gv.pitch_stat_types)
    except Exception as e:
        # accept any types of errors
        el.error_logger(e, 'Re-assign Columns: ' + str(e), team, year)
        return False

    try:
        # write to BATTING stats database
        update_time = t.time()
        conn.fast_executemany = True
        # print(bat_stats.head)
        bat_stats.to_sql('batting', conn, if_exists='append', index=False)
        print('Import BATTING STATS to Database: ', dt.seconds_convert(t.time() - update_time))
    except Exception as e:
        # accept any types of errors
        el.error_logger(e, 'WRITE batting stats: ' + str(e), team, year)
        return False

    try:
        # write to PITCHING stats database
        update_time = t.time()
        conn.fast_executemany = True
        pitch_stats.to_sql('pitching', conn, if_exists='append', index=False)
        print('Import PITCHING STATS to Database: ', dt.seconds_convert(t.time() - update_time))
    except Exception as e:
        # accept any types of errors
        el.error_logger(e, 'WRITE pitching stats: ' + str(e), team, year)
        return False

    try:
        # write to FIELDING stats database
        update_time = t.time()
        conn.fast_executemany = True
        pitch_stats.to_sql('fielding', conn, if_exists='append', index=False)
        print('Import FIELDING STATS to Database: ', dt.seconds_convert(t.time() - update_time))
    except Exception as e:
        # accept any types of errors
        el.error_logger(e, 'WRITE fielding stats: ' + str(e), team, year)
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
        el.error_logger(e, 'WRITE stats performance: ' + str(e), team, year)
        return False

    # send completion notice
    conn.fast_executemany = True
    finish_str = {
        'process_name': 'stat_processor',
        'data_year': year,
        'team_name': team,
        'time_elapsed': t2_time - t1_time,
        'timestamp': t.strftime("%Y-%m-%d %H:%M:%S", t.localtime())
    }
    completion = pd.DataFrame([finish_str])
    completion.to_sql('process_log', conn, if_exists='append', index=False)

    return True
'''


# splitting the generate_stats function into separate jobs => separate functions
def generate_stats2(year, stat_category):

    t1_time = t.time()

    try:
        # retrieve the game player stats
        conn = dbs.engine.connect()
        output = conn.execute("SELECT * FROM raw_player_stats WHERE data_year=? AND bat_pitch=?",
                              year, stat_category).fetchall()
        idx = 0
        # conversion time
        conv_time = t.time()
        for x in output:
            gv.player[idx] = dict(x)
            idx += 1
        print('Conversion Time:', dt.seconds_convert(t.time() - conv_time))
    except Exception as e:
        # accept any types of errors
        el.error_logger(e, 'Query & Convert Raw Player Stats: ' + str(e), 'ALL', year, stat_category)
        return False

    try:
        gv.player_stats = sc.stat_organizer2(gv.player, stat_category)
    except Exception as e:
        # accept any types of errors
        el.error_logger(e, 'STAT_ORGANIZER: ' + str(e), 'ALL', year, stat_category)
        return False

    try:
        # reassign column names
        gen_stats = gv.player_stats[stat_category]
        if stat_category == 'batting':
            gen_stats.rename(columns=gv.bat_stat_types)
        elif stat_category == 'pitching':
            gen_stats.rename(columns=gv.pitch_stat_types)
        elif stat_category == 'fielding':
            gen_stats.rename(columns=gv.field_stat_types)
    except Exception as e:
        # accept any types of errors
        el.error_logger(e, 'Re-assign Columns: ' + str(e), 'ALL', year, stat_category)
        return False

    try:
        # write the STATS to corresponding database
        update_time = t.time()
        conn.fast_executemany = True
        gen_stats.to_sql(stat_category, conn, if_exists='append', index=False)
        print('Import', stat_category.upper(), 'STATS to Database: ', dt.seconds_convert(t.time() - update_time))
    except Exception as e:
        # accept any type of errors
        el.error_logger(e, 'WRITE stats: ' + str(e), 'ALL', year, stat_category)

    try:
        # WRITING STATS PERFORMANCE
        t2_time = t.time()
        fgp = open('GAMEPLAY.LOG', mode='a')
        fgp.write('Stats Processing: ' + str(dt.seconds_convert(t2_time - t1_time)) + '\n')
        print('Stats Processing: ', dt.seconds_convert(t2_time - t1_time))
        fgp.close()
    except Exception as e:
        # accept any types of errors
        el.error_logger(e, 'WRITE stats performance: ' + str(e), 'ALL', year, stat_category)
        return False

    # send completion notice
    conn.fast_executemany = True
    finish_str = {
        'process_name': 'stat_processor: ' + stat_category,
        'data_year': year,
        'team_name': 'ALL',
        'time_elapsed': t2_time - t1_time,
        'timestamp': t.strftime("%Y-%m-%d %H:%M:%S", t.localtime())
    }
    completion = pd.DataFrame([finish_str])
    completion.to_sql('process_log', conn, if_exists='append', index=False)

    return True
