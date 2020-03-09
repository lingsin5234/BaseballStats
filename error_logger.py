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


# processing errors function
def processing_errors(error, process_name, team_name, data_year, game_id, half_inning):

    c = dbs.engine.connect()
    error_dict = {
        'process_name': process_name,
        'data_year': data_year,
        'team_name': team_name,
        'game_id': game_id,
        'half_inning': half_inning,
        'error': error,
        'timestamp': t.strftime("%Y-%m-%d %H:%M:%S", t.localtime())
    }
    query = "INSERT INTO processing_errors ('process_name', 'data_year', 'team_name', 'game_id', " \
            "'error', 'timestamp') VALUES (?,?,?,?,?,?)"
    c.execute(query, list(error_dict.values()))


# test error logger
# error_logger('TEST ERROR', 'play_processor', 'BOS', '2018')

# test processing errors
# processing_errors('TEST ERROR', 'play_processor', 'BOS', '2018', 'BOS201805200', '2_1')
