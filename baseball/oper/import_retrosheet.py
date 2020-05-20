# this python script is to import the retrosheet files
from os import path, mkdir, remove
import sys
import time as t
import pandas as pd
import urllib.request
from zipfile import ZipFile as zf
from . import global_variables as gv
from . import error_logger as el
from . import db_setup as dbs
from . import date_time as dt
from . import extract_teams_players as etp


# if len(sys.argv) > 1:
def import_data(year):

    t1_time = t.time()
    year = str(year)  # force into a string

    # create import folder if not available
    if path.exists(gv.data_dir):
        pass
    else:
        mkdir(gv.data_dir)

    # create landing folder if not available
    if path.exists(gv.data_dir + '/landing'):
        pass
    else:
        mkdir(gv.data_dir + '/landing')

    # download file into import/landing folder
    url = 'https://www.retrosheet.org/events/'
    # year = sys.argv[1]
    zip_file = year + 'eve.zip'
    urllib.request.urlretrieve(url+zip_file, gv.data_dir + '/landing/'+zip_file)

    # create new folder for the unzipped contents
    if path.exists(gv.data_dir + '/' + year):
        pass
    else:
        mkdir(gv.data_dir + '/' + year)

    # unzip contents to the year folder
    try:
        with zf(gv.data_dir + '/landing/'+zip_file) as unzip:
            unzip.extractall(gv.data_dir + '/' + year)
    except Exception as e:
        # accept any types of errors
        el.error_logger(e, 'unzipping import year: ' + str(e), None, year)
        return False

    # remove landing file
    try:
        if path.exists(gv.data_dir + '/landing/' + zip_file):
            remove(gv.data_dir + '/landing/' + zip_file)
    except Exception as e:
        # accept any types of errors
        el.error_logger(e, 'removing landing file: ' + str(e), None, year)
        return False

    t2_time = t.time()

    # send completion notice
    conn = dbs.engine.connect()
    conn.fast_executemany = True
    finish_str = {
        'process_name': 'import_year',
        'data_year': year,
        'team_name': '---',
        'time_elapsed': t2_time - t1_time,
        'timestamp': t.strftime("%Y-%m-%d %H:%M:%S", t.localtime())
    }
    completion = pd.DataFrame([finish_str])
    completion.to_sql('process_log', conn, if_exists='append', index=False)

    # now that import is done; run the teams/players extractions
    status = etp.extract_teams(year)
    if status:
        status = etp.extract_players(year)
        if not status:
            return False
    else:
        return False

    return True
