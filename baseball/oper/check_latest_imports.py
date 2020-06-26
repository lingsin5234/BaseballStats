# this file will check for the latest imports and what has been processed into the database
# this script is called periodically to keep the database and performance in check
import sys
import os
import numpy as np
from django import forms
from . import db_setup as dbs
from . import date_time as dt
from . import global_variables as gv
from . import database_reader as dr


# check teams remaining in year
def check_teams(year, which_process):

    # query
    c = dbs.engine.connect()

    # num of roster files
    all_files = os.listdir(gv.data_dir + '/' + str(year))
    rosters = [f for f in all_files if '.ROS' in f]

    # ignore all-stars
    rosters = [r for r in rosters if 'ALS' not in r and 'NLS' not in r]

    # list the team names from the roster files
    teams = [x.replace(str(year)+'.ROS', '') for x in rosters]

    if which_process == 'process_team':

        # check which teams have been processed for "this" year
        query = "SELECT team_name FROM process_log WHERE data_year=? AND process_name='play_processor'"
        results = c.execute(query, year).fetchall()
        results = [r for r, in results]

        if len(results) == len(teams):
            # print("All teams processed, check stats generated")
            return None
        else:
            # find missing teams
            missing_teams_pp = [t for t in teams if t not in results]
            # print("Play Processing Incomplete! Still missing teams:")
            # print(missing_teams_pp)
            return missing_teams_pp

    # check gen_stats  ---- THIS WON'T WORK ANYMORE ---- no more TEAM NAME
    elif which_process == 'generate_stats':

        # next, check to see if the teams were processed at all
        query = "SELECT team_name FROM process_log WHERE data_year=? AND process_name LIKE 'stat_processor%'"
        results = c.execute(query, year).fetchall()
        results = [r for r, in results]

        if len(results) != len(teams):
            missing_teams_stats = [t for t in teams if t not in results]
            # print("Teams not passed by stats_processor:")
            # print(missing_teams_stats)
            return missing_teams_stats
        else:
            # all teams stats generated
            return None

    # check which teams to generate stats for
    elif which_process == 'go_generate_stats':

        # need list of those processed already but NOT generated stats for
        query = "SELECT team_name FROM process_log WHERE data_year=? AND process_name='play_processor'"
        results = c.execute(query, year).fetchall()
        results = [r for r, in results]
        print("HERE ARE PROCESSED:", results)

        query = "SELECT team_name FROM process_log WHERE data_year=? AND process_name LIKE 'stat_processor%'"
        completed = c.execute(query, year).fetchall()
        completed = [r for r, in completed]
        print("HERE ARE COMPLETED: ", completed)

        results = list(np.setdiff1d(results, completed))
        print("HERE ARE RESULTS: ", results)

        return results

    # check the total list of teams
    elif which_process == 'total_num_teams':

        return len(teams)

    # check for view_stats
    else:
        # next, check to see if the teams were processed at all
        query = "SELECT team_name FROM process_log WHERE data_year=? AND process_name LIKE 'stat_processor%'"
        results = c.execute(query, year).fetchall()
        results = [r for r, in results]

        return results


# check which years have yet to be imported
def check_years():

    years = dt.gen_year()
    all_dir = os.listdir(gv.data_dir)

    # list the year dir
    year_dir = [int(y) for y in all_dir if y.isnumeric()]
    year_dir.sort()

    # get the list of years still not imported
    missing_years = list(np.setdiff1d(years, [int(i) for i in year_dir]))

    return missing_years


# get the years that have been imported already
def get_years():

    all_dir = os.listdir(gv.data_dir)

    # list the year dir
    year_dir = [int(y) for y in all_dir if y.isnumeric()]
    year_dir.sort()

    return year_dir


# return year choices
def get_year_choices():

    year_choices = [(0, 0)]
    missing_years = check_years()
    if missing_years is None:
        year = forms.ChoiceField(required=True, label='Year', choices=year_choices)
    else:
        missing_years.sort()
        missing_years.reverse()
        year_choices = [(m, m) for m in missing_years]
        year = forms.ChoiceField(required=True, label='Year', choices=year_choices)

    return [year, year_choices]


# return team choices
def get_team_choices(which_process):

    year_choices = [(0, 0)]
    team_choices = [('---', '---')]

    # get years that have already been imported
    all_dir = os.listdir('baseball/import')
    imported_years = [int(y) for y in all_dir if y.isnumeric()]
    imported_years.sort()

    # check if anything there
    if imported_years is None:
        year = forms.ChoiceField(required=True, label='Year', choices=year_choices)
        team = forms.ChoiceField(required=True, label='Team', choices=team_choices)
    else:
        imported_years.reverse()
        year_choices = [(i, i) for i in imported_years]
        year = forms.ChoiceField(required=True, label='Year', choices=year_choices)

        # check for teams for all years selected
        processed_teams = []
        for y in imported_years:
            p_teams = check_teams(str(y), which_process)
            if p_teams is None:
                pass
            else:
                processed_teams.extend(p_teams)
                # print(which_process, ': ', processed_teams)

        processed_teams = sorted(np.unique(processed_teams))
        team_choices = [(t, t) for t in processed_teams]
        team = forms.ChoiceField(required=True, label='Team', choices=team_choices)

    return [year, year_choices, team, team_choices]


# return year choices - version 2
def get_year_choices2():

    # only batting for now
    query = "SELECT DISTINCT data_year FROM player_year_team WHERE stat_category='batting' ORDER BY data_year desc"
    results = dr.baseball_db_reader(query)
    results = [r for r, in results]

    # remember to assign them as tuples
    year_choices = [(y, y) for y in results]
    # print("Get Year Choices 2: ", year_choices)

    return year_choices


# return team choices - version 2
def get_team_choices2(year):

    # only batting for now
    query = 'SELECT DISTINCT team_name FROM player_year_team WHERE data_year=' + str(year) + ' ORDER BY team_name'
    results = dr.baseball_db_reader(query)
    results = [r for r, in results]

    # remember to assign them as tuples
    team_choices = [(t, t) for t in results]
    # print("Get Team Choices 2: ", team_choices)

    query = 'SELECT COUNT(*) FROM players'
    conn = dbs.engine.connect()
    results = conn.execute(query).fetchall()
    # print("Players", results)
    conn.close()

    return team_choices


# get a list of years that have fully completed processing but not done stats generation
def get_process_complete_years():

    # get list of years from process
    conn = dbs.engine.connect()
    query = 'SELECT data_year, COUNT(DISTINCT team_name) FROM process_log WHERE team_name IS NOT ? GROUP BY data_year'
    years = conn.execute(query, '---').fetchall()
    print("Done Teams:", years)

    # get all team count per year
    query = 'SELECT data_year, COUNT(DISTINCT team_id) FROM teams GROUP BY data_year'
    teams = conn.execute(query).fetchall()
    print("Total Teams:", teams)
    conn.close()

    # get all years from stats generated
    stats_gen = get_stats_gen_complete_years()

    # check how many team names loaded for particular year vs. stat years
    done = [y for (y, c) in teams if (y, c) in years]
    stats_not_done = [y for y in done if y not in stats_gen]
    print(done, stats_not_done)

    return stats_not_done


# get list of years that have completed stats generation
def get_stats_gen_complete_years():

    # get all years from stats generated
    conn = dbs.engine.connect()
    query = 'SELECT DISTINCT data_year FROM player_year_team GROUP BY data_year'
    stats_gen = conn.execute(query).fetchall()
    stats_gen = [r for (r, ) in stats_gen]
    print("STATS GEN", stats_gen)
    conn.close()

    return stats_gen
