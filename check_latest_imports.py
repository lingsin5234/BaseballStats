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
    query = "SELECT team_name FROM process_log WHERE data_year=? AND process_name='stat_processor'"
    results = c.execute(query, year).fetchall()

    # num of roster files
    all_files = os.listdir('import/' + year)
    rosters = [f for f in all_files if '.ROS' in f]

    # list the team names from the roster files
    teams = [x.replace(year+'.ROS', '') for x in rosters]
    results = [r for r, in results]

    if len(results) == len(teams):
        print("All teams processed, stats generated.")
    else:
        # find missing teams
        missing_teams = [t for t in teams if t not in results]
        print("Incomplete! Still missing teams.")
        print(missing_teams)
