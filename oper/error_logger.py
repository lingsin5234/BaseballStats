# this file is for error logging functionality
import time as t
from . import db_setup as dbs


# error logging function
def error_logger(error, process_name, team_name, data_year, stat_category):

    c = dbs.engine.connect()
    error_dict = {
        'process_name': process_name,
        'data_year': data_year,
        'team_name': team_name,
        'stat_category': stat_category,
        'error': str(error),
        'timestamp': t.strftime("%Y-%m-%d %H:%M:%S", t.localtime())
    }
    query = "INSERT INTO error_log ('process_name', 'data_year', 'team_name', 'stat_category', 'error', 'timestamp')" \
            " VALUES (?,?,?,?,?,?)"
    c.execute(query, list(error_dict.values()))
    # c.close()

    return True


# processing errors function
def processing_errors(error, process_name, team_name, data_year, game_id, half_inning):

    c = dbs.engine.connect()
    error_dict = {
        'process_name': process_name,
        'data_year': str(data_year),
        'team_name': team_name,
        'game_id': game_id,
        'half_inning': half_inning,
        'error': error,
        'timestamp': t.strftime("%Y-%m-%d %H:%M:%S", t.localtime())
    }
    query = "INSERT INTO processing_errors ('process_name', 'data_year', 'team_name', 'game_id', " \
            "'half_inning', 'error', 'timestamp') VALUES (?,?,?,?,?,?,?)"
    c.execute(query, list(error_dict.values()))
    # c.close()

    return True

# test error logger
# error_logger('TEST ERROR', 'play_processor', 'BOS', '2018')

# test processing errors
# processing_errors('TEST ERROR', 'play_processor', 'BOS', '2018', 'BOS201805200', '2_1')
