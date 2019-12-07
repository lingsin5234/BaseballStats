# libraries
import global_variables as gv


# stat collector
def stat_collector(player_id, game_id, stat_type, stat_value):

    # modify player table
    gv.player.loc[-1] = [player_id, game_id, stat_type, stat_value]
    gv.player.index = gv.player.index + 1

    return True


# stat organizer
def stat_organizer(player_tb):

    player_tb = player_tb.groupby(['player_id', 'stat_type']).size().reset_index()

    return player_tb


# game start tracker
def game_tracker():

    return
