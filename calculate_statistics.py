# this script processes the statistics from the processed imports
import time as t
import sys
import global_variables as gv
import stat_collector as sc
import date_time as dt
import db_setup as dbs

if len(sys.argv) > 1:

    t1_time = t.time()

    # retrieve the game player stats
    conn = dbs.engine.connect()
    team_id = sys.argv[1] + '%'
    output = conn.execute("SELECT * FROM raw_player_stats WHERE game_id LIKE ?", team_id).fetchall()
    idx = 0
    # conversion time
    conv_time = t.time()
    for x in output:
        gv.player[idx] = dict(x)
        idx += 1
    print('Conversion Time:', dt.seconds_convert(t.time() - conv_time))
    gv.player_stats = sc.stat_organizer(gv.player)

    # separate batting and pitching stats, reassign column names
    bat_stats = gv.player_stats['batting']
    pitch_stats = gv.player_stats['pitching']
    bat_stats = bat_stats.rename(columns=gv.bat_stat_types)
    print(bat_stats.head())
    exit()

    # write to BATTING stats database
    update_time = t.time()
    conn.fast_executemany = True
    bat_stats.to_sql('batting', conn, if_exists='append', index=False)
    print('Import BATTING STATS to Database: ', dt.seconds_convert(t.time() - update_time))

    # write to PITCHING stats database
    update_time = t.time()
    conn.fast_executemany = True
    bat_stats.to_sql('pitching', conn, if_exists='append', index=False)
    print('Import PITCHING STATS to Database: ', dt.seconds_convert(t.time() - update_time))

    # WRITING STATS PERFORMANCE
    t2_time = t.time()
    fgp = open('GAMEPLAY.LOG', mode='a')
    fgp.write('Stats Processing: ' + str(dt.seconds_convert(t2_time - t1_time)) + '\n')
    print('Stats Processing: ', dt.seconds_convert(t2_time - t1_time))
    fgp.close()
