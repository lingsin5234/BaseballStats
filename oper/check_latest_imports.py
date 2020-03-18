# this file will check for the latest imports and what has been processed into the database
# this script is called periodically to keep the database and performance in check
import sys
import os
import numpy as np
from . import db_setup as dbs
from . import date_time as dt


# check teams remaining in year
def check_teams():

    # check for cmd-line arguments
    if len(sys.argv) > 1:

        year = sys.argv[1]

        # query
        c = dbs.engine.connect()
        query = "SELECT team_name FROM process_log WHERE data_year=? AND process_name='play_processor'"
        results = c.execute(query, year).fetchall()
        results = [r for r, in results]

        # num of roster files
        all_files = os.listdir('import/' + year)
        rosters = [f for f in all_files if '.ROS' in f]

        # list the team names from the roster files
        teams = [x.replace(year+'.ROS', '') for x in rosters]

        if len(results) == len(teams):
            print("All teams processed, check stats generated")
        else:
            # find missing teams
            missing_teams_pp = [t for t in teams if t not in results]
            print("Play Processing Incomplete! Still missing teams:")
            print(missing_teams_pp)
            exit()

        # next, check to see if the teams were processed at all
        query = "SELECT team_name FROM process_log WHERE data_year=? AND process_name='play_processor'"
        results = c.execute(query, year).fetchall()
        results = [r for r, in results]

        if len(results) != len(teams):
            missing_teams_stats = [t for t in teams if t not in results]
            print("Teams not passed by stats_processor:")
            print(missing_teams_stats)
            return True

    else:
        print("Missing Year Argument in CMD")
        return False


# check which years have yet to be imported
def check_years():

    years = dt.gen_year()
    all_dir = os.listdir('baseball/import')

    # list the year dir
    year_dir = [y for y in all_dir if y.isnumeric()]

    # get the list of years still not imported
    missing_years = list(np.setdiff1d(years, [int(i) for i in year_dir]))
    # print(missing_years)

    return missing_years


# check_years()
