# this script extracts the teams and players from the roster files
import os
import pandas as pd
import time as t
from . import global_variables as gv
from . import error_logger as el
from . import db_setup as dbs
from . import class_structure as cl
from . import date_time as dt


# extract teams for single year
def extract_teams(year):

    s_time = t.time()

    # check for team inside import YEAR:
    file_str = gv.data_dir + '/' + str(year) + '/TEAM' + str(year)
    if os.path.exists(file_str):
        pass
    else:
        el.error_logger('NO TEAM FILE', str(year) + ' needs to be imported first!', year)
        return False

    # open the file and list all the teams
    try:
        f = open(file_str, 'r')
        f1 = f.readlines()
        f1 = [f.replace('\n', '').split(',') for f in f1]
        teams_list = []
        for tm in f1:
            teams_list.append(dict(zip(['team_id', 'league_id', 'city_name', 'name_of_team'], tm)))
        f.close()

    except Exception as e:
        # accept any types of errors
        el.error_logger(e, 'I/O Open Retrosheet Event File', '', year)
        return False

    # process to data frame
    try:
        teams = pd.DataFrame.from_dict(teams_list)
        teams['data_year'] = year
        teams['team_name'] = teams['city_name'] + ' ' + teams['name_of_team']

        # write the teams to sql database
        print(teams.to_dict('records'))
        conn = dbs.engine.connect()
        insert_time = t.time()
        conn.execute(cl.teams.insert(), teams.to_dict('records'))
        print('Import TEAMS to Database:', dt.seconds_convert(t.time() - insert_time))

        # send completion notice for STARTERS
        conn.fast_executemany = True
        finish_str = {
            'process_name': 'team_names_import',
            'data_year': year,
            'team_name': None,
            'time_elapsed': t.time() - s_time,
            'timestamp': t.strftime("%Y-%m-%d %H:%M:%S", t.localtime())
        }
        completion = pd.DataFrame([finish_str])
        completion.to_sql('process_log', conn, if_exists='append', index=False)

    except Exception as e:
        # accept any types of errors
        el.error_logger(e, 'team_names_import', '', year)
        return False

    return True


# extract players for single year
def extract_players(year):

    # check for import YEAR:
    dir_str = gv.data_dir + '/' + str(year)
    if os.path.exists(dir_str):
        pass
    else:
        el.error_logger('NO IMPORT YEAR', str(year) + ' needs to be imported first!', year)
        return False

    # get all the team rosters except All-Star
    all_files = os.listdir(dir_str)
    rosters = [r for r in all_files if '.ROS' in r]
    print(rosters)

    return True


# extract_teams(2019)
# extract_players(2019)
