# this script processes the statistics from the processed imports
import time as t
import global_variables as gv
import stat_collector as sc
import date_time as dt

t1_time = t.time()

# retrieve the game player stats
# gv.player = pd.read_csv('PRE_STATS.csv')
gv.player_stats = sc.stat_organizer(gv.player)
gv.player_stats['batting'].to_csv('BATTING.csv', sep=',', index=False)
gv.player_stats['pitching'].to_csv('PITCHING.csv', sep=',', index=False)

# WRITING STATS PERFORMANCE
t2_time = t.time()
fgp = open('GAMEPLAY.LOG', mode='a')
fgp.write('Stats Processing: ' + str(dt.seconds_convert(t2_time - t1_time)) + '\n')
print('Stats Processing: ', dt.seconds_convert(t2_time - t1_time))
fgp.close()
