# this script processes the imported files
# using the extract_data.py file as reference
import pandas as pd
import re
import os
import sys
import time as t
import game_converter as g
import play_processor as pp
import stat_collector as sc
import global_variables as gv
import date_time as dt
import sqlite3 as sql
import db_setup as dbs
import class_structure as cl


# extract data for single team
def extract_data_single_team(year, team):

    # open and read data files
    dir_str = 'import/' + str(year)
    # for event_file in os.listdir(dir_str):
    # print(x)
    # file_dir = dir_str + '/' + event_file
    all_files = os.listdir(dir_str)

    # search for team
    file_nm = [f for f in all_files if str(year) + team in f]

    # start timer
    s_time = t.time()

    # get current file
    file_dir = dir_str + '/' + file_nm[0]
    f = open(file_dir, "r")
    f1 = f.readlines()

    # collect id and group the games
    games = []
    game_ids = []
    game_info = []
    game_play = []
    game_start = []
    for line_item in f1:
        # Do this check first: if end of file OR (line item is ID and game_play > 0)
        if (line_item.index == f1[-1].index) | ((line_item[:2] == "id") & (len(game_play) > 0)):
            # populate game info, starts, plays
            game_info.append(game_start.copy())
            game_info.append(game_play.copy())
            games.append(game_info.copy())
            game_info.clear()
            game_start.clear()
            game_play.clear()  # Needed to clear this so it doesn't tack on for all remaining games!

        # separate this game with the next
        if line_item[:2] == "id":
            # append game id
            game_ids.append(line_item)
            game_info.append(line_item)
        elif line_item[:4] == "play" or line_item[:3] == "sub":
            game_play.append(line_item)
        elif line_item[:5] == "start":
            game_start.append(line_item)
        else:
            game_info.append(line_item)

    # close the read file
    f.close()
    f1 = None

    # extract all starting lineups by game (replaced each iteration in the variable)
    gv.game_roster = sc.game_tracker(games)
    games_roster = pd.DataFrame(gv.game_roster).transpose()
    # games_roster.to_csv('STARTERS.csv', sep=',', mode='a', index=False)

    # write the lineups to database
    c = dbs.engine.connect()
    c.execute(cl.starters.insert(), games_roster)

    exit()

    # insert row by row
    # all_values = list(games_roster.itertuples(index=False, name=None))
    # for i, v in enumerate(all_values):
    #     print(str(i / len(all_values) * 100) + '%...')
    #     c.execute('''INSERT INTO starters
    #                     VALUES (?,?,?,?,?,?,?)''', v)
    #     conn.commit()

    # convert all games for 1 file
    a_full_df = g.convert_games(games, games_roster)

    # play_processor2 function
    for e, each_game in enumerate(a_full_df):
        # game performance
        a1_time = t.time()

        # then run the processor
        this_game = pp.play_processor3(each_game, games_roster)

        # game performance
        a2_time = t.time()

        # reindex the DICTIONARY keys
        this_game = dict((int(k) + gv.fo_idx, value) for (k, value) in this_game.items())
        gv.fo_idx += len(this_game)

        # game performance
        a3_time = t.time()

        # store into full_output
        gv.full_output.update(this_game)

        # game performance
        a4_time = t.time()
        fgp = open('GAMEPLAY.LOG', mode='a')
        fgp.write('GAME #:' + str(e) + ' process: ' + str(dt.seconds_convert(a2_time - a1_time)) + '\n')
        fgp.write('GAME #:' + str(e) + ' reindex: ' + str(dt.seconds_convert(a3_time - a2_time)) + '\n')
        fgp.write('GAME #:' + str(e) + ' store: ' + str(dt.seconds_convert(a4_time - a3_time)) + '\n')
        fgp.write('GAME #:' + str(e) + ' TOTAL: ' + str(dt.seconds_convert(a4_time - a1_time)) + '\n')
        print('GAME #:', e, ' TOTAL: ', a4_time - a1_time)
        fgp.close()

    # testing play_processor3
    # pd.DataFrame(gv.full_output).transpose().to_csv('OUTPUT.csv', sep=',', mode='a', index=False)
    # exit()

    # indicator of what is completed
    e_time = t.time()
    print('COMPLETED: ', file_nm[0], ' - ', dt.seconds_convert(e_time - s_time))
    fgp = open('GAMEPLAY.LOG', mode='a')
    fgp.write('COMPLETED: ' + file_nm[0] + ' - ' + str(dt.seconds_convert(e_time - s_time)) + '\n')
    fgp.close()

    # Write Output File after converting entire list of dict to data frame
    transpose_time = t.time()
    import_to_sql = pd.DataFrame.from_dict(gv.full_output).transpose()
    print('Transposing takes: ', dt.seconds_convert(t.time() - transpose_time))
    # print(import_to_sql)

    # update database
    update_time = t.time()
    c.fast_executemany = True
    import_to_sql.to_sql('gameplay', conn, if_exists='replace', index=False)
    print('Import to Database: ', dt.seconds_convert(t.time() - update_time))

    o1_time = t.time()


# extract one full year
def extract_data_year(year):

    # open and read data files
    dir_str = 'import/' + str(year)
    # for event_file in os.listdir(dir_str):
    # print(x)
    # file_dir = dir_str + '/' + event_file
    all_files = os.listdir(dir_str)

    for file_nm in all_files:
        # start timer
        s_time = t.time()

        # get current file
        file_dir = dir_str + '/' + file_nm
        f = open(file_dir, "r")
        f1 = f.readlines()

        # collect id and group the games
        games = []
        game_ids = []
        game_info = []
        game_play = []
        game_start = []
        for line_item in f1:
            # Do this check first: if end of file OR (line item is ID and game_play > 0)
            if (line_item.index == f1[-1].index) | ((line_item[:2] == "id") & (len(game_play) > 0)):
                # populate game info, starts, plays
                game_info.append(game_start.copy())
                game_info.append(game_play.copy())
                games.append(game_info.copy())
                game_info.clear()
                game_start.clear()
                game_play.clear()  # Needed to clear this so it doesn't tack on for all remaining games!

            # separate this game with the next
            if line_item[:2] == "id":
                # append game id
                game_ids.append(line_item)
                game_info.append(line_item)
            elif line_item[:4] == "play" or line_item[:3] == "sub":
                game_play.append(line_item)
            elif line_item[:5] == "start":
                game_start.append(line_item)
            else:
                game_info.append(line_item)

        # close the read file
        f.close()
        f1 = None

        # extract all starting lineups by game (replaced each iteration in the variable)
        gv.game_roster = sc.game_tracker(games)
        games_roster = pd.DataFrame(gv.game_roster).transpose()
        games_roster.to_csv('STARTERS.csv', sep=',', mode='a', index=False)

        # convert all games for 1 file
        a_full_df = g.convert_games(games, games_roster)

        # play_processor2 function
        for e, each_game in enumerate(a_full_df):
            # game performance
            a1_time = t.time()

            # then run the processor
            this_game = pp.play_processor3(each_game, games_roster)

            # game performance
            a2_time = t.time()

            # reindex the DICTIONARY keys
            this_game = dict((int(k) + gv.fo_idx, value) for (k, value) in this_game.items())
            gv.fo_idx += len(this_game)

            # game performance
            a3_time = t.time()

            # store into full_output
            gv.full_output.update(this_game)

            # game performance
            a4_time = t.time()
            fgp = open('GAMEPLAY.LOG', mode='a')
            fgp.write('GAME #:' + str(e) + ' process: ' + str(dt.seconds_convert(a2_time - a1_time)) + '\n')
            fgp.write('GAME #:' + str(e) + ' reindex: ' + str(dt.seconds_convert(a3_time - a2_time)) + '\n')
            fgp.write('GAME #:' + str(e) + ' store: ' + str(dt.seconds_convert(a4_time - a3_time)) + '\n')
            fgp.write('GAME #:' + str(e) + ' TOTAL: ' + str(dt.seconds_convert(a4_time - a1_time)) + '\n')
            # print('GAME #:', e, ' TOTAL: ', a4_time - a1_time)
            fgp.close()

        # testing play_processor3
        # pd.DataFrame(gv.full_output).transpose().to_csv('OUTPUT.csv', sep=',', mode='a', index=False)
        # exit()

        # indicator of what is completed
        e_time = t.time()
        print('COMPLETED: ', file_nm, ' - ', dt.seconds_convert(e_time - s_time))
        fgp = open('GAMEPLAY.LOG', mode='a')
        fgp.write('COMPLETED: ' + file_nm + ' - ' + str(dt.seconds_convert(e_time - s_time)) + '\n')
        fgp.close()

    # Write Output File after converting entire list of dict to data frame
    o1_time = t.time()


# actually run the functions
extract_data_single_team(2018, 'ANA')
