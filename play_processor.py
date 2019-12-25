# libraries
import re
import stat_collector as sc
import global_variables as gv
import base_running as br
import pandas as pd
import time as t
import pitcher_oper as po


# re-write the processor based on re.search/re.findall grep searching
def play_processor2(game_num, the_df):

    # performance
    q0_time = t.time()

    # the game id
    the_game_id = the_df.at[0, 'game_id']

    # store the starting lineup for this game
    lineup = gv.game_roster[gv.game_roster.game_id == the_game_id]

    # convert df to dictionary
    fgp = open('GAMEPLAY.LOG', mode='a')
    qa_time = t.time()
    the_dict = the_df.to_dict('records')  # ## actual convert task ##
    qb_time = t.time()
    fgp.write('Pre-play Prep: ' + str(qa_time - q0_time) + '\n')
    fgp.write('CONVERT DICT: ' + str(qb_time - qa_time) + '\n')
    fgp.close()

    for i, this_line in enumerate(the_dict):

        # performance checkpoint
        q1_time = t.time()

        # check for new inning
        if i > 0:
            if this_line['half_innings'] == the_dict[i-1]['half_innings']:
                this_line['1B_before'] = the_dict[i-1]['1B_after']
                this_line['2B_before'] = the_dict[i-1]['2B_after']
                this_line['3B_before'] = the_dict[i-1]['3B_after']
                this_line['outs'] = the_dict[i-1]['outs']
            else:
                # see if pass works
                pass

        # performance checkpoint
        q2_time = t.time()

        # for plays
        if this_line['type'] == 'play':

            # take out any ! in play
            this_line['play'] = this_line['play'].replace('!', '')

            # assign the pitcher
            this_line['pitcherID'] = po.assign_pitcher(lineup, this_line, False)[0]

            # store player_id, the play, and pitcher_id
            pid = this_line['playerID']
            the_play = this_line['play']
            hid = this_line['pitcherID']
            print(hid, this_line['half_innings'])

            # Case 1: regular single out plays - exclude SH/SF
            if bool(re.search(r'^[1-9]([1-9!]+)?/(G|F|L|P|BG|BP|BL|IF)(?!/(SH|SF))', the_play)) | \
                    bool(re.search(r'^[1-9]([1-9!]+)?$', the_play)):
                this_line['outs'] += 1

                # stat add: AB, PA, LOB, RLSP
                st = ['AB', 'PA', 'LOB', 'RLSP']
                sc.stat_collector(pid, this_line, st)

                # pitch add: IP, BF
                # pt = ['IP', 'BF']
                # sc.pitch_collector(hid, this_line, pt)

            # Case 2: irregular put-outs, runner is specified
            # i.e. when put out at base not normally covered by that fielder
            elif re.search(r'^[1-9]([1-9]+)?\([B123]\)/(?!FO)', the_play):
                this_line['outs'] += 1

                # determine which runner
                if re.search(r'^[1-9]([1-9]+)?\(B\)', the_play):
                    # out is at 1B, no action required
                    pass
                elif re.search(r'^[1-9]([1-9]+)?\([123]\)', the_play):
                    # take a look
                    print(the_game_id, ': ', the_play)

                # stat add: AB, PA, LOB, RLSP
                st = ['AB', 'PA', 'LOB', 'RLSP']
                sc.stat_collector(pid, this_line, st)

            # Case 3: explicit force out plays
            elif re.search(r'^[1-9]([1-9]+)?\([B123]\)/FO', the_play):
                this_line['outs'] += 1

                # determine which runner
                if re.search(r'^[1-9]([1-9]+)?\(B\)', the_play):
                    # mark an X for processing later.
                    this_line['1B_after'] = 'X'
                elif re.search(r'^[1-9]([1-9]+)?\(1\)', the_play):
                    # mark an X for processing later.
                    this_line['2B_after'] = 'X'
                elif re.search(r'^[1-9]([1-9]+)?\(2\)', the_play):
                    # mark an X for processing later.
                    this_line['3B_after'] = 'X'
                elif re.search(r'^[1-9]([1-9]+)?\(3\)', the_play):
                    # out at Home, no action required
                    pass

                # stat add: AB, PA, LOB, RLSP
                st = ['AB', 'PA', 'LOB', 'RLSP']
                sc.stat_collector(pid, this_line, st)

            # Case 4: sacrifice hit / fly
            elif re.search(r'^[1-9]([1-9]+)?.*/(SH|SF)', the_play):
                this_line['outs'] += 1

                # stat add: SH/SF, PA
                if re.search(r'SF', the_play):
                    st = ['SF', 'PA']
                else:
                    st = ['SH', 'PA']
                sc.stat_collector(pid, this_line, st)

            # Case 5: fielders' choice
            elif re.search(r'^FC[1-9]', the_play):
                # determine if there was an out
                if re.search(r'[123]X[123H](?!\(([0-9]+)?E([0-9]+)?\))', the_play):
                    this_line['outs'] += 1
                
                # move batter if explicitly mentioned
                if re.search(r'B-2', the_play):
                    this_line['2B_after'] = pid
                elif re.search(r'B-3', the_play):
                    this_line['3B_after'] = pid
                elif re.search(r'B-H', the_play):
                    this_line['runs_scored'] += 1
                    st = ['R']
                    sc.stat_collector(pid, this_line, st)
                
                # batter is out!
                elif re.search(r'BX[123H]', the_play):
                    this_line['outs'] += 1
                else:
                    this_line['1B_after'] = pid

                # stat add: AB, PA, LOB, RLSP
                st = ['AB', 'PA', 'LOB', 'RLSP']
                sc.stat_collector(pid, this_line, st)

            # Case 6: strike out with NO event
            elif re.search(r'^K([1-9]+)?(?!\+)', the_play):
                this_line['outs'] += 1

                # stat add: AB, K, PA, LOB, RLSP
                st = ['AB', 'K', 'PA', 'LOB', 'RLSP']
                sc.stat_collector(pid, this_line, st)

            # Case 7: strike out + event
            elif re.search(r'^K\+', the_play):
                this_line['outs'] += 1

                # determine if next play is out or not.
                # determine which base stolen
                if re.search(r'SB', the_play):
                    the_df.loc[[i]] = br.steal_processor(this_line)

                # determine which base runner was caught
                elif re.search(r'CS', the_play):
                    this_line['outs'] += 1
                    this_line = br.steal_processor(this_line)

                # if explicitly moves the batter on passed ball or WP
                elif re.search(r'(WP|PB)\..*B-[123H]', the_play):
                    this_line['outs'] -= 1
                    if re.search(r'\..*B-1', the_play):
                        this_line['1B_after'] = pid
                    elif re.search(r'\..*B-2', the_play):
                        this_line['2B_after'] = pid
                    elif re.search(r'\..*B-3', the_play):
                        this_line['3B_after'] = pid
                    elif re.search(r'\..*B-H', the_play):
                        this_line['runs_scored'] = pid

                # otherwise PB that moves other runners or Defensive Indifference
                elif re.search(r'(WP|PB|DI)\.', the_play):
                    # batter is still out -- i think
                    pass

                # similar case for WP, no batter movement
                elif re.search(r'WP\..*[123]-[123H]', the_play):
                    # batter is still out.
                    pass

                # Pick Off Error
                elif re.search(r'PO[123]\(([0-9]+)?E([0-9]+)?\)', the_play):
                    # batter is still out.
                    pass

                # Pick Off DP
                elif re.search(r'PO[123].*/DP', the_play):
                    # runner is also out
                    this_line['outs'] += 1

                    if re.search(r'PO1', the_play):
                        this_line['1B_after'] = 'X'
                    if re.search(r'PO2', the_play):
                        this_line['2B_after'] = 'X'
                    if re.search(r'PO3', the_play):
                        this_line['3B_after'] = 'X'

                # Other DP
                elif re.search(r'.*/DP', the_play):
                    # a runner is also out
                    # this_line['outs'] += 1 -- this is already recorded
                    pass

                # else
                else:
                    # out applies anyway; no action required
                    print('Game #: ', the_game_id, 'CHECK HERE: ', the_play)

                # stat add: AB, K, PA, LOB, RLSP
                st = ['AB', 'K', 'PA', 'LOB', 'RLSP']
                sc.stat_collector(pid, this_line, st)

            # Case 8: routine double plays
            elif re.search(r'.*DP', the_play):
                this_line['outs'] += 2

                # determine which runners are out
                if re.search(r'\(1\)', the_play):
                    this_line['2B_after'] = 'X'
                if re.search(r'\(2\)', the_play):
                    this_line['3B_after'] = 'X'
                if re.search(r'\([123]\).*\([123]\)', the_play):
                    # nothing happens if 3rd base runner is out.
                    # both 1 and 2 would be recorded
                    pass
                else:
                    # record the out at 1st implicitly if only 1 other baserunner is out.
                    this_line['1B_after'] = 'X'

                # stat add: AB, PA, LOB, RLSP
                st = ['AB', 'PA', 'LOB', 'RLSP']
                sc.stat_collector(pid, this_line, st)

            # Case 9: triple plays
            elif re.search(r'.*TP', the_play):
                this_line['outs'] += 3

                # stat add: AB, PA, LOB, RLSP
                st = ['AB', 'PA', 'LOB', 'RLSP']
                sc.stat_collector(pid, this_line, st)

            # Case 10: catcher interference or pitcher/1B interference
            elif re.search(r'^C/E[1-9]', the_play):
                this_line['1B_after'] = pid

                # stat add: PA
                st = ['PA']
                sc.stat_collector(pid, this_line, st)

            # Case 11: hit! -- the fielder(s) after letter is optional; HIT + Errors are Resolved here too.
            elif re.search(r'^((S|D|T)([1-9]+)?/?|H/|HR|DGR)', the_play):
                # print('A Hit!: ', the_play)

                # determine what type of hit.
                if re.search(r'^S([1-9]+)?', the_play):

                    # stat add: AB, PA, H
                    st = ['AB', 'PA', 'H']

                    # check if batter advanced elsewhere - e.g. Error on Throw / Catch
                    if re.search(r'B-[23H]', the_play):
                        if re.search(r'B-2', the_play):
                            this_line['2B_after'] = pid
                        elif re.search(r'B-3', the_play):
                            this_line['3B_after'] = pid
                        elif re.search(r'B-H', the_play):
                            this_line['runs_scored'] += 1
                            st.append('R')
                    else:
                        this_line['1B_after'] = pid
                    sc.stat_collector(pid, this_line, st)

                elif re.search(r'^(D([1-9]+)?|DGR)', the_play):

                    # stat add: AB, PA, H, D
                    st = ['AB', 'PA', 'H', 'D']

                    # check if batter advanced elsewhere
                    if re.search(r'B-[3H]', the_play):
                        if re.search(r'B-3', the_play):
                            this_line['3B_after'] = pid
                        elif re.search(r'B-H', the_play):
                            this_line['runs_scored'] += 1
                            st.append('R')
                    else:
                        this_line['2B_after'] = pid
                    sc.stat_collector(pid, this_line, st)

                elif re.search(r'^T([1-9]+)?', the_play):

                    # stat add: AB, PA, H, T
                    st = ['AB', 'PA', 'H', 'T']

                    # check if batter advanced elsewhere
                    if re.search(r'B-H', the_play):
                        this_line['runs_scored'] += 1
                        st.append('R')
                    else:
                        this_line['3B_after'] = pid
                    sc.stat_collector(pid, this_line, st)

                else:
                    this_line['runs_scored'] += 1

                    # stat add: AB, PA, H, HR, R
                    st = ['AB', 'PA', 'H', 'HR', 'R']

                    # score the RBI if not NR or NORBI
                    if not (re.search(r'B-H\((NR|NORBI)\)', the_play)):
                        st.append('RBI')
                    sc.stat_collector(pid, this_line, st)

            # Case 12: walk or hit by pitch
            elif re.search(r'^(HP|IW|W(?!P))(?!\+)', the_play):
                # print('Walk / Hit By Pitch: ', the_play)
                this_line['1B_after'] = pid

                # stat add: PA, W or HBP
                st = ['PA']
                if re.search(r'^HP', the_play):
                    st.append('HBP')
                elif re.search(r'^IW', the_play):
                    st.append('IW')
                    st.append('W')
                else:
                    st.append('W')
                sc.stat_collector(pid, this_line, st)

            # Case 13: walk + event
            elif re.search(r'^(HP|IW|W(?!P))\+', the_play):
                # print('Walk + Event: ', the_play)
                this_line['1B_after'] = pid

                # stat add: PA, W or HBP
                st = ['PA']
                if re.search(r'^HP', the_play):
                    st.append('HBP')
                elif re.search(r'^IW', the_play):
                    st.append('IW')
                    st.append('W')
                else:
                    st.append('W')
                sc.stat_collector(pid, this_line, st)

                # DOES NOT DO ANYTHING ELSE!??!?! #

            # Case 14: error on FOUL fly ball
            elif re.search(r'^FLE[1-9]', the_play):
                # print('FOUL Fly ball Error: ', the_play)
                pass

            # Case 15: error on ball in play
            elif re.search(r'^([1-9]+)?E[1-9]', the_play):
                # print('Error: ', the_play)

                # stat add: AB, PA
                st = ['AB', 'PA']

                # if explicitly puts moves the batter
                if re.search(r'\..*B(-|X)[123H]', the_play):
                    if re.search(r'\..*B-1', the_play):
                        this_line['1B_after'] = pid
                    elif re.search(r'\..*B-2', the_play):
                        this_line['2B_after'] = pid
                    elif re.search(r'\..*B-3', the_play):
                        this_line['3B_after'] = pid
                    elif re.search(r'\..*B-H', the_play):
                        this_line['runs_scored'] += 1
                        # stat add: R
                        st.append('R')
                        # score the RBI if not NR or NORBI
                        if not(re.search(r'B-H\((NR|NORBI)\)', the_play)):
                            st.append('RBI')
                    # other cases are BX[123H] - just ignore
                else:
                    # assume they reached first base safely
                    this_line['1B_after'] = pid

                sc.stat_collector(pid, this_line, st)

            # Case 16: wild pitch or balk
            elif re.search(r'^(WP|BK)', the_play):
                # print('Wild Pitch: ', the_play)
                pass

            # Case 17: no pitch
            elif re.search(r'^NP$', the_play):
                pass

            # Case 18: stolen base
            elif re.search(r'^SB', the_play):
                # print('Stolen Base: ', the_play)
                this_line = br.steal_processor(this_line)

            # Case 19: defensive indifference
            elif re.search(r'^DI', the_play):
                # print('Defensive Indiff.: ', the_play)
                pass

            # Case 20: caught stealing
            elif re.search(r'^CS', the_play):
                # print('Caught Stealing: ', the_play)
                this_line['outs'] += 1
                this_line = br.steal_processor(this_line)

            # Case 21: pick off and/or caught stealing
            elif re.search(r'^PO(CS)?[123H]', the_play):
                # print('Picked Off &/ Caught Stealing: ', the_play)
                this_line['outs'] += 1
                this_line = br.steal_processor(this_line)

            # Case 22: passed ball
            elif re.search(r'^PB', the_play):
                # print('Passed Ball: ', the_play)
                pass

            # Case 23: unexpected runner advance
            elif re.search(r'^OA', the_play):
                # print('Unexpected Runner Adv.: ', the_play)
                pass

            # Case 24: batter interference
            elif re.search(r'([1-9]+)/BINT', the_play):
                # print('Batter Interference: ', the_play)
                pass

            # Case 25: Hit with some errors
            # Moved to HITS - Case #11

            # Case 26: appeal plays
            elif re.search(r'.*AP', the_play):
                # print('Appeal Play not already overridden: ', the_play)
                pass

            # Case 20: ELSE
            else:
                print('Game #: ', the_game_id, 'CASE NEEDED: ', the_play)

            # HANDLING BASERUNNERS
            this_line = br.base_running(this_line)

        # this line item is substitution
        else:
            this_line['1B_after'] = the_df.at[i - 1, '1B_before']
            this_line['2B_after'] = the_df.at[i - 1, '2B_before']
            this_line['3B_after'] = the_df.at[i - 1, '3B_before']
            this_line['outs'] = the_df.at[i - 1, 'outs']

            # if pinch-runner, put in the runner
            # batting team = the half inning
            if this_line['half'] == this_line['team_id']:

                # pinch runner only
                if this_line['fielding'] == '12':

                    # check which spot in the lineup, get the playerID:
                    sub_filter = (lineup.team_id == this_line['team_id']) & \
                                 (lineup.bat_lineup == this_line['batting'])
                    sub_index = lineup.index[sub_filter]
                    sub_player_id = lineup.at[sub_index[0], 'player_id']

                    # check the bases for the runner:
                    if this_line['1B_after'] == sub_player_id:
                        this_line['1B_after'] = pid
                    elif this_line['2B_after'] == sub_player_id:
                        this_line['2B_after'] = pid
                    elif this_line['3B_after'] == sub_player_id:
                        this_line['3B_after'] = pid
                    else:
                        # most likely is Pinch Hitting -- make a check for this later; but should be '11'
                        pass

                    # replace the person in the lineup
                    lineup.at[sub_index[0], 'player_id'] = pid
                    lineup.at[sub_index[0], 'player_nm'] = this_line['name']

                # pinch hitter only
                elif this_line['fielding'] == '11':

                    # check which spot in the lineup, get the playerID:
                    sub_filter = (lineup.team_id == this_line['team_id']) & \
                                 (lineup.bat_lineup == this_line['batting'])
                    sub_index = lineup.index[sub_filter]

                    # replace the person in the lineup
                    lineup.at[sub_index[0], 'player_id'] = pid
                    lineup.at[sub_index[0], 'player_nm'] = this_line['name']

            # fielding team = the half inning
            else:
                # check for only the pitching substitutions for now
                if this_line['fielding'] == '1':
                    pitch_index = po.assign_pitcher(lineup, this_line, True)[1]
                    lineup.at[pitch_index, 'player_id'] = this_line['playerID']
                    lineup.at[pitch_index, 'player_nm'] = this_line['name']

        # performance checkpoint
        q3_time = t.time()

        # set the line back to the df to be stored properly.
        the_dict[i] = this_line

        # performance checkpoint
        q4_time = t.time()

        # store to log
        fgp = open('GAMEPLAY.LOG', mode='a')

        # performance review
        fgp.write('LINE #' + str(i) + '\n')
        fgp.write('setup: ' + str(q2_time - q1_time) + '\n')
        fgp.write('play/sub: ' + str(q3_time - q2_time) + '\n')
        fgp.write('reassign: ' + str(q4_time - q3_time) + '\n')
        fgp.write('total: ' + str(q4_time - q1_time) + '\n')
        fgp.close()

    # return the dictionary converted back as data frame
    return pd.DataFrame(the_dict)
