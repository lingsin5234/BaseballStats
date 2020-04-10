# this file is to run tests of the oper files ONLY
from . import import_retrosheet as ir
from . import process_imports as pi
from . import generate_statistics as gs
from . import aggregate_statistics as ag
from . import database_reader as dr
import os

'''
# import Year; print True if completed
print("Import Completed: ", ir.import_data(2018))

# print True if this succeeds
files = os.listdir('baseball/import/2018')
files = [f[4:7] for f in files if f.find('ROS') == -1 and f.find('TEAM') == -1]
for f in files:
    # print("Processing Completed: ", f, pi.process_data_single_team(2018, f))
    # print(f)
    print("Stats Generated: ", f, gs.generate_stats(2018, f))
'''
'''
# ^ above done wrong. should be processing ALL stats before doing a generate stats!
query = "SELECT DISTINCT game_id FROM raw_player_stats"
results = dr.baseball_db_reader(query)
print(results)
'''
# print True if aggregate_statistics is completed
print("Statistics Aggregated: ", ag.stats_aggregate())

