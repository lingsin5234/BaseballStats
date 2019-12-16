# libraries
import re
import stat_collector as sc
import global_variables as gv
import base_running as br


# re-write the processor based on re.search/re.findall grep searching
def play_processor2(game_num, the_df):

    # the game id
    the_game_id = the_df.at[0, 'game_id']

    # store the starting lineup for this game
    lineup = gv.game_roster[gv.game_roster.game_id == the_game_id]

    # print(the_df.index)
    # process would go line by line.
    for i in the_df.index:

        # check for new inning
        if i > 0:
            if the_df.at[i, 'half_innings'] == the_df.at[i-1, 'half_innings']:
                the_df.at[i, '1B_before'] = the_df.at[i-1, '1B_after']
                the_df.at[i, '2B_before'] = the_df.at[i-1, '2B_after']
                the_df.at[i, '3B_before'] = the_df.at[i-1, '3B_after']
                the_df.at[i, 'outs'] = the_df.at[i-1, 'outs']
            else:
                # see if pass works
                pass

        # store the entire row of game_play
        this_line = the_df.loc[[i]]

        # for plays
        if the_df.at[i, 'type'] == 'play':

            # store player_id
            pid = the_df.at[i, 'playerID']

            # Case 1: regular single out plays - exclude SH/SF
            if re.search(r'^[1-9]([1-9!]+)?/(G|F|L|P|BG|BP|BL)(?!/(SH|SF))', the_df.at[i, 'play']):
                # print('Routine Put Out: ', the_df.at[i, 'play'])
                the_df.at[i, 'outs'] += 1

                # stat add: AB, PA, LOB, RLSP
                st = ['AB', 'PA', 'LOB', 'RLSP']
                sc.stat_collector(pid, this_line, st)

            # Case 2: irregular put-outs, runner is specified
            # i.e. when put out at base not normally covered by that fielder
            elif re.search(r'^[1-9]([1-9]+)?\([B123]\)/(?!FO)', the_df.at[i, 'play']):
                # print('Irregular Put Out: ', the_df.at[i, 'play'])
                the_df.at[i, 'outs'] += 1

                # determine which runner
                if re.search(r'^[1-9]([1-9]+)?\(B\)', the_df.at[i, 'play']):
                    # out is at 1B, no action required
                    pass
                elif re.search(r'^[1-9]([1-9]+)?\([123]\)', the_df.at[i, 'play']):
                    # take a look
                    print(the_game_id, ': ', the_df.at[i, 'play'])

                # stat add: AB, PA, LOB, RLSP
                st = ['AB', 'PA', 'LOB', 'RLSP']
                sc.stat_collector(pid, this_line, st)

            # Case 3: explicit force out plays
            elif re.search(r'^[1-9]([1-9]+)?\([B123]\)/FO', the_df.at[i, 'play']):
                # print('Force Out: ', the_df.at[i, 'play'])
                the_df.at[i, 'outs'] += 1

                # determine which runner
                if re.search(r'^[1-9]([1-9]+)?\(B\)', the_df.at[i, 'play']):
                    # mark an X for processing later.
                    the_df.at[i, '1B_after'] = 'X'
                elif re.search(r'^[1-9]([1-9]+)?\(1\)', the_df.at[i, 'play']):
                    # mark an X for processing later.
                    the_df.at[i, '2B_after'] = 'X'
                elif re.search(r'^[1-9]([1-9]+)?\(2\)', the_df.at[i, 'play']):
                    # mark an X for processing later.
                    the_df.at[i, '3B_after'] = 'X'
                elif re.search(r'^[1-9]([1-9]+)?\(3\)', the_df.at[i, 'play']):
                    # out at Home, no action required
                    pass

                # stat add: AB, PA, LOB, RLSP
                st = ['AB', 'PA', 'LOB', 'RLSP']
                sc.stat_collector(pid, this_line, st)

            # Case 4: sacrifice hit / fly
            elif re.search(r'^[1-9]([1-9]+)?.*/(SH|SF)', the_df.at[i, 'play']):
                # print('Sac Hit/Fly: ', the_df.at[i, 'play'])
                the_df.at[i, 'outs'] += 1

                # stat add: SH/SF, PA
                if re.search(r'SF', the_df.at[i, 'play']):
                    st = ['SF', 'PA']
                else:
                    st = ['SH', 'PA']
                sc.stat_collector(pid, this_line, st)

            # Case 5: fielders' choice
            elif re.search(r'^FC[1-9]', the_df.at[i, 'play']):
                # print('Fielders\' Choice: ', the_df.at[i, 'play'])

                # determine if there was an out
                if re.search(r'[123]X[123H](?!\(([0-9]+)?E([0-9]+)?\))', the_df.at[i, 'play']):
                    the_df.at[i, 'outs'] += 1
                # move batter if explicitly mentioned
                if re.search(r'B-2', the_df.at[i, 'play']):
                    the_df.at[i, '2B_after'] = pid
                elif re.search(r'B-3', the_df.at[i, 'play']):
                    the_df.at[i, '3B_after'] = pid
                elif re.search(r'B-H', the_df.at[i, 'play']):
                    the_df.at[i, 'runs_scored'] += 1
                    st = ['R']
                    sc.stat_collector(pid, this_line, st)
                # batter is out!
                elif re.search(r'BX[123H]', the_df.at[i, 'play']):
                    the_df.at[i, 'outs'] += 1
                else:
                    the_df.at[i, '1B_after'] = pid

                # stat add: AB, PA, LOB, RLSP
                st = ['AB', 'PA', 'LOB', 'RLSP']
                sc.stat_collector(pid, this_line, st)

            # Case 6: strike out with NO event
            elif re.search(r'^K([1-9]+)?(?!\+)', the_df.at[i, 'play']):
                # print('STRIKEOUT: ', the_df.at[i, 'play'])
                the_df.at[i, 'outs'] += 1

                # stat add: AB, K, PA, LOB, RLSP
                st = ['AB', 'K', 'PA', 'LOB', 'RLSP']
                sc.stat_collector(pid, this_line, st)

            # Case 7: strike out + event
            elif re.search(r'^K\+', the_df.at[i, 'play']):
                # print('Strikeout + Event: ', the_df.at[i, 'play'])
                the_df.at[i, 'outs'] += 1

                # determine if next play is out or not.
                # determine which base stolen
                if re.search(r'SB', the_df.at[i, 'play']):
                    the_df.loc[[i]] = br.steal_processor(this_line)
                    # new_line = br.steal_processor(this_line)
                    # the_df.at[i, '1B_after'] = new_line[0]
                    # the_df.at[i, '2B_after'] = new_line[1]
                    # the_df.at[i, '3B_after'] = new_line[2]
                    # the_df.at[i, 'runs_scored'] = new_line[3]

                # determine which base runner was caught
                elif re.search(r'CS', the_df.at[i, 'play']):
                    the_df.at[i, 'outs'] += 1
                    the_df.loc[[i]] = br.steal_processor(this_line)

                # if explicitly moves the batter on passed ball or WP
                elif re.search(r'(WP|PB)\..*B-[123H]', the_df.at[i, 'play']):
                    the_df.at[i, 'outs'] -= 1
                    if re.search(r'\..*B-1', the_df.at[i, 'play']):
                        the_df.at[i, '1B_after'] = the_df.at[i, 'playerID']
                    elif re.search(r'\..*B-2', the_df.at[i, 'play']):
                        the_df.at[i, '2B_after'] = the_df.at[i, 'playerID']
                    elif re.search(r'\..*B-3', the_df.at[i, 'play']):
                        the_df.at[i, '3B_after'] = the_df.at[i, 'playerID']
                    elif re.search(r'\..*B-H', the_df.at[i, 'play']):
                        the_df.at[i, 'runs_scored'] = the_df.at[i, 'playerID']

                # similar case for WP, no batter movement
                elif re.search(r'WP\..*[123]-[123H]', the_df.at[i, 'play']):
                    # batter is still out.
                    pass

                # else
                else:
                    # out applies anyway; no action required
                    print('Game #: ', the_game_id, 'CHECK HERE: ', the_df.at[i, 'play'])

                # stat add: AB, K, PA, LOB, RLSP
                st = ['AB', 'K', 'PA', 'LOB', 'RLSP']
                sc.stat_collector(pid, this_line, st)

            # Case 8: routine double plays
            elif re.search(r'.*DP', the_df.at[i, 'play']):
                # print('DOUBLE PLAY: ', the_df.at[i, 'play'])
                the_df.at[i, 'outs'] += 2

                # determine which runners are out
                if re.search(r'\(1\)', the_df.at[i, 'play']):
                    the_df.at[i, '2B_after'] = 'X'
                if re.search(r'\(2\)', the_df.at[i, 'play']):
                    the_df.at[i, '3B_after'] = 'X'
                if re.search(r'\([123]\).*\([123]\)', the_df.at[i, 'play']):
                    # nothing happens if 3rd base runner is out.
                    # both 1 and 2 would be recorded
                    pass
                else:
                    # record the out at 1st implicitly if only 1 other baserunner is out.
                    the_df.at[i, '1B_after'] = 'X'

                # stat add: AB, PA, LOB, RLSP
                st = ['AB', 'PA', 'LOB', 'RLSP']
                sc.stat_collector(pid, this_line, st)

            # Case 9: triple plays
            elif re.search(r'.*TP', the_df.at[i, 'play']):
                # print('TRIPLE PLAY: ', the_df.at[i, 'play'])
                the_df.at[i, 'outs'] += 3

                # stat add: AB, PA, LOB, RLSP
                st = ['AB', 'PA', 'LOB', 'RLSP']
                sc.stat_collector(pid, this_line, st)

            # Case 10: catcher interference or pitcher/1B interference
            elif re.search(r'^C/E[1-9]', the_df.at[i, 'play']):
                # print('Catcher Int.: ', the_df.at[i, 'play'])
                the_df.at[i, '1B_after'] = the_df.at[i, 'playerID']

                # stat add: PA
                st = ['PA']
                sc.stat_collector(pid, this_line, st)

            # Case 11: hit! -- the fielder(s) after letter is optional; HIT + Errors are Resolved here too.
            elif re.search(r'^((S|D|T)([1-9]+)?/|H/|HR|DGR)', the_df.at[i, 'play']):
                # print('A Hit!: ', the_df.at[i, 'play'])

                # determine what type of hit.
                if re.search(r'^S([1-9]+)?', the_df.at[i, 'play']):

                    # stat add: AB, PA, H
                    st = ['AB', 'PA', 'H']

                    # check if batter advanced elsewhere - e.g. Error on Throw / Catch
                    if re.search(r'B-[23H]', the_df.at[i, 'play']):
                        if re.search(r'B-2', the_df.at[i, 'play']):
                            the_df.at[i, '2B_after'] = pid
                        elif re.search(r'B-3', the_df.at[i, 'play']):
                            the_df.at[i, '3B_after'] = pid
                        elif re.search(r'B-H', the_df.at[i, 'play']):
                            the_df.at[i, 'runs_scored'] += 1
                            st.append('R')
                    else:
                        the_df.at[i, '1B_after'] = pid
                    sc.stat_collector(pid, this_line, st)

                elif re.search(r'^(D([1-9]+)?|DGR)', the_df.at[i, 'play']):

                    # stat add: AB, PA, H, D
                    st = ['AB', 'PA', 'H', 'D']

                    # check if batter advanced elsewhere
                    if re.search(r'B-[3H]', the_df.at[i, 'play']):
                        if re.search(r'B-3', the_df.at[i, 'play']):
                            the_df.at[i, '3B_after'] = pid
                        elif re.search(r'B-H', the_df.at[i, 'play']):
                            the_df.at[i, 'runs_scored'] += 1
                            st.append('R')
                    else:
                        the_df.at[i, '2B_after'] = pid
                    sc.stat_collector(pid, this_line, st)

                elif re.search(r'^T([1-9]+)?', the_df.at[i, 'play']):

                    # stat add: AB, PA, H, T
                    st = ['AB', 'PA', 'H', 'T']

                    # check if batter advanced elsewhere
                    if re.search(r'B-H', the_df.at[i, 'play']):
                        the_df.at[i, 'runs_scored'] += 1
                        st.append('R')
                    else:
                        the_df.at[i, '3B_after'] = pid
                    sc.stat_collector(pid, this_line, st)

                else:
                    the_df.at[i, 'runs_scored'] += 1

                    # stat add: AB, PA, H, HR, R
                    st = ['AB', 'PA', 'H', 'HR', 'R']

                    # score the RBI if not NR or NORBI
                    if not (re.search(r'B-H\((NR|NORBI)\)', the_df.at[i, 'play'])):
                        st.append('RBI')
                    sc.stat_collector(pid, this_line, st)

            # Case 12: walk or hit by pitch
            elif re.search(r'^(HP|IW|W(?!P))(?!\+)', the_df.at[i, 'play']):
                # print('Walk / Hit By Pitch: ', the_df.at[i, 'play'])
                the_df.at[i, '1B_after'] = the_df.at[i, 'playerID']

                # stat add: PA, W or HBP
                st = ['PA']
                if re.search(r'^HP', the_df.at[i, 'play']):
                    st.append('HBP')
                elif re.search(r'^IW', the_df.at[i, 'play']):
                    st.append('IW')
                    st.append('W')
                else:
                    st.append('W')
                sc.stat_collector(pid, this_line, st)

            # Case 13: walk + event
            elif re.search(r'^(HP|IW|W(?!P))\+', the_df.at[i, 'play']):
                # print('Walk + Event: ', the_df.at[i, 'play'])
                the_df.at[i, '1B_after'] = the_df.at[i, 'playerID']

                # stat add: PA, W or HBP
                st = ['PA']
                if re.search(r'^HP', the_df.at[i, 'play']):
                    st.append('HBP')
                elif re.search(r'^IW', the_df.at[i, 'play']):
                    st.append('IW')
                    st.append('W')
                else:
                    st.append('W')
                sc.stat_collector(pid, this_line, st)

                # DOES NOT DO ANYTHING ELSE!??!?! #

            # Case 14: error on FOUL fly ball
            elif re.search(r'^FLE[1-9]', the_df.at[i, 'play']):
                # print('FOUL Fly ball Error: ', the_df.at[i, 'play'])
                pass

            # Case 15: error on ball in play
            elif re.search(r'^([1-9]+)?E[1-9]', the_df.at[i, 'play']):
                # print('Error: ', the_df.at[i, 'play'])

                # stat add: AB, PA
                st = ['AB', 'PA']

                # if explicitly puts moves the batter
                if re.search(r'\..*B(-|X)[123H]', the_df.at[i, 'play']):
                    if re.search(r'\..*B-1', the_df.at[i, 'play']):
                        the_df.at[i, '1B_after'] = the_df.at[i, 'playerID']
                    elif re.search(r'\..*B-2', the_df.at[i, 'play']):
                        the_df.at[i, '2B_after'] = the_df.at[i, 'playerID']
                    elif re.search(r'\..*B-3', the_df.at[i, 'play']):
                        the_df.at[i, '3B_after'] = the_df.at[i, 'playerID']
                    elif re.search(r'\..*B-H', the_df.at[i, 'play']):
                        the_df.at[i, 'runs_scored'] += 1
                        # stat add: R
                        st.append('R')
                        # score the RBI if not NR or NORBI
                        if not(re.search(r'B-H\((NR|NORBI)\)', the_df.at[i, 'play'])):
                            st.append('RBI')
                    # other cases are BX[123H] - just ignore
                else:
                    # assume they reached first base safely
                    the_df.at[i, '1B_after'] = the_df.at[i, 'playerID']

                sc.stat_collector(pid, this_line, st)

            # Case 16: wild pitch or balk
            elif re.search(r'^(WP|BK)', the_df.at[i, 'play']):
                # print('Wild Pitch: ', the_df.at[i, 'play'])
                pass

            # Case 17: no pitch
            elif re.search(r'^NP$', the_df.at[i, 'play']):
                pass

            # Case 18: stolen base
            elif re.search(r'^SB', the_df.at[i, 'play']):
                # print('Stolen Base: ', the_df.at[i, 'play'])
                the_df.loc[[i]] = br.steal_processor(this_line)

            # Case 19: defensive indifference
            elif re.search(r'^DI', the_df.at[i, 'play']):
                # print('Defensive Indiff.: ', the_df.at[i, 'play'])
                pass

            # Case 20: caught stealing
            elif re.search(r'^CS', the_df.at[i, 'play']):
                # print('Caught Stealing: ', the_df.at[i, 'play'])
                the_df.at[i, 'outs'] += 1
                the_df.loc[[i]] = br.steal_processor(this_line)

            # Case 21: pick off and/or caught stealing
            elif re.search(r'^PO(CS)?[123H]', the_df.at[i, 'play']):
                # print('Picked Off &/ Caught Stealing: ', the_df.at[i, 'play'])
                the_df.at[i, 'outs'] += 1

                if re.search(r'CS2', the_df.at[i, 'play']):
                    # stat add: CS
                    st = ['CS']
                    sc.stat_collector(the_df.at[i, '1B_before'], this_line, st)

                if re.search(r'CS3', the_df.at[i, 'play']):
                    # stat add: CS
                    st = ['CS']
                    sc.stat_collector(the_df.at[i, '2B_before'], this_line, st)

                if re.search(r'CSH', the_df.at[i, 'play']):
                    # stat add: CS
                    st = ['CS']
                    sc.stat_collector(the_df.at[i, '3B_before'], this_line, st)

            # Case 22: passed ball
            elif re.search(r'^PB', the_df.at[i, 'play']):
                # print('Passed Ball: ', the_df.at[i, 'play'])
                pass

            # Case 23: unexpected runner advance
            elif re.search(r'^OA', the_df.at[i, 'play']):
                # print('Unexpected Runner Adv.: ', the_df.at[i, 'play'])
                pass

            # Case 24: batter interference
            elif re.search(r'([1-9]+)/BINT', the_df.at[i, 'play']):
                # print('Batter Interference: ', the_df.at[i, 'play'])
                pass

            # Case 25: Hit with some errors
            # Moved to HITS - Case #11

            # Case 26: appeal plays
            elif re.search(r'.*AP', the_df.at[i, 'play']):
                # print('Appeal Play not already overridden: ', the_df.at[i, 'play'])
                pass

            # Case 20: ELSE
            else:
                print('Game #: ', the_game_id, 'CASE NEEDED: ', the_df.at[i, 'play'])

            # HANDLING BASERUNNERS
            # always a . before the baserunners move; include batter movement just to skip the ELSE
            if re.search(r'\.[B123](-|X)[123H]', the_df.at[i, 'play']):
                # move the runners that explicitly moved
                if re.search(r'\..*3-3', the_df.at[i, 'play']):
                    the_df.at[i, '3B_after'] = the_df.at[i, '3B_before']
                if re.search(r'\..*3-H', the_df.at[i, 'play']):
                    the_df.at[i, 'runs_scored'] += 1

                    # stat add: R
                    st = ['R']
                    sc.stat_collector(the_df.at[i, '3B_before'], this_line, st)

                    # check rbi awarded or not
                    if bool(re.search(r'3-H([\(UR\)/THE0-9]+)?(\((NR|NORBI)\))', the_df.at[i, 'play'])) | \
                            bool(re.search(r'^FC.*X', the_df.at[i, 'play'])) | \
                            bool(re.search(r'^([1-9]+)?E.*3-H(?!\(RBI\))', the_df.at[i, 'play'])) | \
                            bool(re.search(r'DP|WP', the_df.at[i, 'play'])):
                        # no RBI recorded
                        pass
                    else:
                        # stat add: RBI
                        st = ['RBI']
                        sc.stat_collector(pid, this_line, st)

                if re.search(r'\..*2-2', the_df.at[i, 'play']):
                    the_df.at[i, '2B_after'] = the_df.at[i, '2B_before']
                if re.search(r'\..*2-3', the_df.at[i, 'play']):
                    the_df.at[i, '3B_after'] = the_df.at[i, '2B_before']
                if re.search(r'\..*2-H', the_df.at[i, 'play']):
                    the_df.at[i, 'runs_scored'] += 1

                    # stat add: R
                    st = ['R']
                    sc.stat_collector(the_df.at[i, '2B_before'], this_line, st)

                    # check rbi awarded or not
                    if bool(re.search(r'2-H([\(UR\)/THE0-9]+)?(\((NR|NORBI)\))', the_df.at[i, 'play'])) | \
                            bool(re.search(r'^FC.*X', the_df.at[i, 'play'])) | \
                            bool(re.search(r'^([1-9]+)?E.*2-H(?!\(RBI\))', the_df.at[i, 'play'])) | \
                            bool(re.search(r'DP|WP', the_df.at[i, 'play'])):
                        # no RBI recorded
                        pass
                    else:
                        # stat add: RBI
                        st = ['RBI']
                        sc.stat_collector(pid, this_line, st)

                if re.search(r'\..*1-1', the_df.at[i, 'play']):
                    the_df.at[i, '1B_after'] = the_df.at[i, '1B_before']
                if re.search(r'\..*1-2', the_df.at[i, 'play']):
                    the_df.at[i, '2B_after'] = the_df.at[i, '1B_before']
                if re.search(r'\..*1-3', the_df.at[i, 'play']):
                    the_df.at[i, '3B_after'] = the_df.at[i, '1B_before']
                if re.search(r'\..*1-H', the_df.at[i, 'play']):
                    the_df.at[i, 'runs_scored'] += 1

                    # stat add: R
                    st = ['R']
                    sc.stat_collector(the_df.at[i, '1B_before'], this_line, st)

                    # check rbi awarded or not
                    if bool(re.search(r'1-H([\(UR\)/THE0-9]+)?(\((NR|NORBI)\))', the_df.at[i, 'play'])) | \
                            bool(re.search(r'^FC.*X', the_df.at[i, 'play'])) | \
                            bool(re.search(r'^([1-9]+)?E.*1-H(?!\(RBI\))', the_df.at[i, 'play'])) | \
                            bool(re.search(r'DP|WP', the_df.at[i, 'play'])):
                        # no RBI recorded
                        pass
                    else:
                        # stat add: RBI
                        st = ['RBI']
                        sc.stat_collector(pid, this_line, st)

                # if batter runner scores is explicitly mentioned, but not the Home Run nor Error FIRST cases
                if bool(re.search(r'\..*B-H', the_df.at[i, 'play'])) & \
                    (not(re.search(r'^(H/|HR|([0-9]+)?E)', the_df.at[i, 'play']))):

                    # stat add: R
                    st = ['R']
                    sc.stat_collector(pid, this_line, st)

                    # check rbi awarded or not
                    if bool(re.search(r'B-H([\(UR\)/THE0-9]+)?(\((NR|NORBI)\))', the_df.at[i, 'play'])) | \
                            bool(re.search(r'^FC.*X', the_df.at[i, 'play'])) | \
                            bool(re.search(r'^([1-9]+)?E.*B-H(?!\(RBI\))', the_df.at[i, 'play'])) | \
                            bool(re.search(r'DP|WP', the_df.at[i, 'play'])):
                        # no RBI recorded
                        pass
                    else:
                        # stat add: RBI
                        st = ['RBI']
                        sc.stat_collector(pid, this_line, st)

                # remove runners that are explicitly out
                if re.search(r'\..*1X[123H]', the_df.at[i, 'play']):
                    the_df.at[i, 'outs'] += 1
                if re.search(r'\..*2X[23H]', the_df.at[i, 'play']):
                    the_df.at[i, 'outs'] += 1
                if re.search(r'\..*3X[3H]', the_df.at[i, 'play']):
                    the_df.at[i, 'outs'] += 1

                # handle weird outs for the batter previously marked on base.
                if re.search(r'\..*BX[123H]', the_df.at[i, 'play']):
                    the_df.at[i, 'outs'] += 1

                    # stat add: AB, PA -- if NOT already added on a hit
                    if not(re.search(r'^((S|D|T)([1-9]+)?/|H/|HR|DGR)', the_df.at[i, 'play'])):
                        st = ['AB', 'PA']
                        sc.stat_collector(pid, this_line, st)

                    # handle the now existing runner
                    if the_df.at[i, '1B_after'] == the_df.at[i, 'playerID']:
                        the_df.at[i, '1B_after'] = 'X'
                    if the_df.at[i, '2B_after'] == the_df.at[i, 'playerID']:
                        the_df.at[i, '2B_after'] = 'X'
                    if the_df.at[i, '3B_after'] == the_df.at[i, 'playerID']:
                        the_df.at[i, '3B_after'] = 'X'
                    if re.search(r'(H[1-9]|HR).*\..*BXH', the_df.at[i, 'play']):
                        the_df.at[i, 'runs_scored'] -= 1

                # retain the runners that did not move
                # R3 did not move and was not out
                if bool(not(re.search(r'\..*3(-|X)[3H]', the_df.at[i, 'play']))) & \
                        (the_df.at[i, '3B_after'] != 'X') & \
                        (the_df.at[i, '3B_before'] is not None) & \
                        (the_df.at[i, '3B_after'] != the_df.at[i, 'playerID']):
                    the_df.at[i, '3B_after'] = the_df.at[i, '3B_before']

                # R2 did not move and was not out
                if bool(not(re.search(r'\..*2(-|X)[23H]', the_df.at[i, 'play']))) &\
                        (the_df.at[i, '2B_after'] != 'X') & \
                        (the_df.at[i, '2B_before'] is not None) & \
                        (the_df.at[i, '2B_after'] != the_df.at[i, 'playerID']):
                    the_df.at[i, '2B_after'] = the_df.at[i, '2B_before']

                # R1 did not move and was not out
                if bool(not(re.search(r'\..*1(-|X)[123H]', the_df.at[i, 'play']))) & \
                        (the_df.at[i, '1B_after'] != 'X') & \
                        (the_df.at[i, '1B_before'] is not None) & \
                        (the_df.at[i, '1B_after'] != the_df.at[i, 'playerID']):
                    the_df.at[i, '1B_after'] = the_df.at[i, '1B_before']

            else:
                # no runner movement and not empty value: copy runners
                if not(re.search(r'SB|CS', the_df.at[i, 'play'])):
                    if (the_df.at[i, '1B_after'] != 'X') & (the_df.at[i, '1B_after'] != the_df.at[i, 'playerID']):
                        the_df.at[i, '1B_after'] = the_df.at[i, '1B_before']
                    if (the_df.at[i, '2B_after'] != 'X') & (the_df.at[i, '2B_after'] != the_df.at[i, 'playerID']):
                        the_df.at[i, '2B_after'] = the_df.at[i, '2B_before']
                    if (the_df.at[i, '3B_after'] != 'X') & (the_df.at[i, '3B_after'] != the_df.at[i, 'playerID']):
                        the_df.at[i, '3B_after'] = the_df.at[i, '3B_before']

                # if there was a stolen base/caught stealing, check other bases
                else:
                    # not a double/triple steal then process stand-still runners
                    if not(re.search(r'SB.*SB', the_df.at[i, 'play'])):
                        if re.search(r'SB2(?!\.)', the_df.at[i, 'play']):
                            if (the_df.at[i, '3B_before'] is not None) & (the_df.at[i, '3B_after'] is None):
                                the_df.at[i, '3B_after'] = the_df.at[i, '3B_before']
                        if re.search(r'SB3(?!\.)', the_df.at[i, 'play']):
                            if (the_df.at[i, '1B_before'] is not None) & (the_df.at[i, '1B_after'] is None):
                                the_df.at[i, '1B_after'] = the_df.at[i, '1B_before']
                        if re.search(r'SBH(?!\.)', the_df.at[i, 'play']):
                            if (the_df.at[i, '1B_before'] is not None) & (the_df.at[i, '1B_after'] is None):
                                the_df.at[i, '1B_after'] = the_df.at[i, '1B_before']
                            if (the_df.at[i, '2B_before'] is not None) & (the_df.at[i, '2B_after'] is None):
                                the_df.at[i, '2B_after'] = the_df.at[i, '2B_before']

            # some combination of out(s)
            if re.search(r'FO|FC|DP', the_df.at[i, 'play']):

                # find the out, move appropriate
                # R1 is out
                if re.search(r'\(1\)', the_df.at[i, 'play']):
                    # batter on first unless DP
                    if the_df.at[i, '1B_after'] != 'X':
                        the_df.at[i, '1B_after'] = the_df.at[i, 'playerID']
                # R2 is out
                if re.search(r'\(2\)', the_df.at[i, 'play']):
                    # batter on first unless DP
                    if the_df.at[i, '1B_after'] != 'X':
                        the_df.at[i, '1B_after'] = the_df.at[i, 'playerID']
                    # R1 on 2nd unless DP
                    if (the_df.at[i, '2B_after'] != 'X') & \
                            (the_df.at[i, '2B_after'] is not None):
                        the_df.at[i, '2B_after'] = the_df.at[i, '1B_before']
                    # R3 stays on base
                    if (the_df.at[i, '3B_after'] != 'X') & \
                            (the_df.at[i, '3B_before'] is not None) & \
                            bool(re.search(r'\..*3(-|X)H', the_df.at[i, 'play'])):
                        the_df.at[i, '3B_after'] = the_df.at[i, '3B_before']

                # R3 is out
                if re.search(r'\(3\)', the_df.at[i, 'play']):
                    # batter on first unless DP
                    if the_df.at[i, '1B_after'] != 'X':
                        the_df.at[i, '1B_after'] = the_df.at[i, 'playerID']
                    # R1 on 2nd unless DP
                    if (the_df.at[i, '2B_after'] != 'X') & \
                            (the_df.at[i, '2B_after'] is not None):
                        the_df.at[i, '2B_after'] = the_df.at[i, '1B_before']
                    # R2 on 3rd unless DP
                    if (the_df.at[i, '3B_after'] != 'X') & \
                            (the_df.at[i, '3B_after'] is not None):
                        the_df.at[i, '3B_after'] = the_df.at[i, '2B_before']

            # remove the X's
            if the_df.at[i, '1B_after'] == 'X':
                the_df.at[i, '1B_after'] = None
            if the_df.at[i, '2B_after'] == 'X':
                the_df.at[i, '2B_after'] = None
            if the_df.at[i, '3B_after'] == 'X':
                the_df.at[i, '3B_after'] = None

        # this line item is substitution
        else:
            the_df.at[i, '1B_after'] = the_df.at[i - 1, '1B_before']
            the_df.at[i, '2B_after'] = the_df.at[i - 1, '2B_before']
            the_df.at[i, '3B_after'] = the_df.at[i - 1, '3B_before']
            the_df.at[i, 'outs'] = the_df.at[i - 1, 'outs']

            # if pinch-runner, put in the runner
            # batting team = the half inning
            if the_df.at[i, 'half'] == the_df.at[i, 'team']:

                # pinch runner only
                if the_df.at[i, 'fielding'] == '12':

                    # check which spot in the lineup, get the playerID:
                    sub_filter = (lineup.team == the_df.at[i, 'team']) & (lineup.bat_lineup == the_df.at[i, 'batting'])
                    sub_index = lineup.index[sub_filter]
                    sub_player_id = lineup.at[sub_index[0], 'player_id']

                    # check the bases for the runner:
                    if the_df.at[i, '1B_after'] == sub_player_id:
                        the_df.at[i, '1B_after'] = the_df.at[i, 'playerID']
                    elif the_df.at[i, '2B_after'] == sub_player_id:
                        the_df.at[i, '2B_after'] = the_df.at[i, 'playerID']
                    elif the_df.at[i, '3B_after'] == sub_player_id:
                        the_df.at[i, '3B_after'] = the_df.at[i, 'playerID']
                    else:
                        # most likely is Pinch Hitting -- make a check for this later; but should be '11'
                        pass

                    # replace the person in the lineup
                    lineup.at[sub_index[0], 'player_id'] = the_df.at[i, 'playerID']

                # pinch hitter only
                elif the_df.at[i, 'fielding'] == '11':

                    # check which spot in the lineup, get the playerID:
                    sub_filter = (lineup.team == the_df.at[i, 'team']) & (
                                lineup.bat_lineup == the_df.at[i, 'batting'])
                    sub_index = lineup.index[sub_filter]
                    # sub_player_id = lineup.at[sub_index[0], 'player_id']

                    # replace the person in the lineup
                    lineup.at[sub_index[0], 'player_id'] = the_df.at[i, 'playerID']

    return the_df
