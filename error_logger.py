# this file is for error logging functionality
import time as t
import db_setup as dbs


# error logging function
def error_logger(error, process_name, team_name, data_year):

    c = dbs.engine.connect()
    error_dict = {
        'process_name': process_name,
        'data_year': data_year,
        'team_name': team_name,
        'error': str(error),
        'timestamp': t.strftime("%Y-%m-%d %H:%M:%S", t.localtime())
    }
    query = "INSERT INTO error_log ('process_name', 'data_year', 'team_name', 'error', 'timestamp') VALUES (?,?,?,?,?)"
    c.execute(query, list(error_dict.values()))


# test error logger
error_logger('TEST ERROR', 'play_processor', 'BOS', '2018')
