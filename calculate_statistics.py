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
    output = conn.execute("SELECT * FROM GAMEPLAY WHERE game_id LIKE ?", team_id).fetchall()
    idx = 0
    # conversion time
    conv_time = t.time()
    for x in output:
        gv.player[idx] = dict(x)
        idx += 1
    print('Conversion Time:', dt.seconds_convert(t.time() - conv_time))
    print(gv.player[0])
    # print(dict(gv.player[0]))
    exit()

    gv.player_stats = sc.stat_organizer(gv.player.to_dict())
    gv.player_stats['batting'].to_csv('BATTING.csv', sep=',', index=False)
    gv.player_stats['pitching'].to_csv('PITCHING.csv', sep=',', index=False)

    # WRITING STATS PERFORMANCE
    t2_time = t.time()
    fgp = open('GAMEPLAY.LOG', mode='a')
    fgp.write('Stats Processing: ' + str(dt.seconds_convert(t2_time - t1_time)) + '\n')
    print('Stats Processing: ', dt.seconds_convert(t2_time - t1_time))
    fgp.close()
