# this file will check for the latest imports and what has been processed into the database
# this script is called periodically to keep the database and performance in check
import sys
import os
import db_setup as dbs

# check for cmd-line arguments
if len(sys.argv) > 1:

    year = sys.argv[1]

    # query
    c = dbs.engine.connect()
    results = c.execute("SELECT COUNT(*) FROM process_log WHERE data_year=?", year).fetchall()

    # num of roster files
    all_files = os.listdir('import/' + year)
    rosters = [f for f in all_files if '.ROS' in f]
    if len(results) == len(rosters):
        print("All teams processed, stats generated.")
    else:
        print("Incomplete! Still missing teams.")
