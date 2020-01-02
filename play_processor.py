# libraries
import re
import stat_collector as sc
import global_variables as gv
import base_running as br
import time as t
import pitcher_oper as po
import non_plate_appearance as npa


# re-write the processor based on re.search/re.findall grep searching
def play_processor3(the_dict, games_roster):

    # the game id
    the_game_id = the_dict[0]['game_id']

    # store the starting lineup for this game
    lineup = games_roster[games_roster.game_id == the_game_id]
    lineup = lineup.reset_index(drop=True)

    for i, this_line in enumerate(the_dict.values()):

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

            # bases occupied
            bases_before = br.bases_occupied(this_line)
            gv.bases_after = bases_before

            # divide up beginning scenario with the running scenarios
            split_play = this_line['play'].split('.')
            begin_play = split_play[0]
            run_play = None
            if len(split_play) > 1:
                run_play = split_play[1]

            # divide up begin_play into plate-appearance (PA) plays and non-PA plays
            if bool(re.search(r'^(WP|NP|BK|PB|FLE|OA|SB|CS|PO|DI)', begin_play)):

                # handles all non-PA and running events thereafter
                this_line = npa.non_pa(this_line, begin_play, run_play, lineup, pid, hid)

            # plate-appearance play
            else:

                # if it is a HIT
                if bool(re.search(r'^((S|D|T)([1-9]+)?/?|H/|HR|DGR)', begin_play)):

                    if bool(not(re.search(r'E[0-9]+', begin_play))):

                        # stats
                        st = ['AB', 'PA', 'H']
                        pt = ['BF', 'H']

                        # single
                        if re.search(r'^S', begin_play):
                            this_line['1B_after'] = pid
                            gv.bases_after = 'B' + gv.bases_after
                        # double
                        elif re.search(r'^D', begin_play):
                            this_line['2B_after'] = pid
                            gv.bases_after = '0B' + gv.bases_after
                            st.append('D')
                            pt.append('D')
                        # triple
                        elif re.search(r'^T', begin_play):
                            this_line['3B_after'] = pid
                            gv.bases_after = '00B' + gv.bases_after
                            st.append('T')
                            pt.append('T')
                        # home run
                        else:
                            this_line['runs_scored'] += 1
                            gv.bases_after = '---'
                            st.extend(['HR', 'R', 'RBI'])
                            pt.extend(['HR', 'R', 'ER'])

                        # stat process
                        sc.stat_collector(pid, lineup, this_line, st)
                        po.pitch_collector(hid, lineup, this_line, pt)

                        # base_runner movements
                        this_line = br.base_running2(this_line, run_play, lineup, pid, hid)

                    else:
                        print('Hit + Error on batter:', begin_play, '==', run_play)

                # Walk or Strikeout
                elif bool(re.search(r'^(IW|HBP|W|K)', begin_play)):

                    # handle these scenarios normally
                    if bool(re.search(r'K', begin_play)):
                        this_line['outs'] += 1
                        gv.bases_after = '-' + gv.bases_after

                        st = ['AB', 'PA', 'K']
                        sc.stat_collector(pid, lineup, this_line, st)
                        pt = ['IP', 'BF', 'K']
                        po.pitch_collector(pid, lineup, this_line, pt)

                    elif bool(re.search(r'HBP', begin_play)):
                        gv.bases_after = 'B' + gv.bases_after

                        st = ['PA', 'HBP']
                        sc.stat_collector(pid, lineup, this_line, st)
                        pt = ['BF', 'HBP']
                        po.pitch_collector(pid, lineup, this_line, pt)

                    else:
                        gv.bases_after = 'B' + gv.bases_after

                        st = ['PA', 'W']
                        pt = ['BF', 'BB']
                        if bool(re.search(r'^IW', begin_play)):
                            st.append('IW')
                            pt.append('IBB')
                        sc.stat_collector(pid, lineup, this_line, st)
                        po.pitch_collector(pid, lineup, this_line, pt)

                    # check if additional event happened
                    if bool(re.search(r'\+', begin_play)):

                        # run the NON-PA function
                        this_line = npa.non_pa(this_line, begin_play, run_play, lineup, pid, hid)

                    # if no batter movements, then put batter on first!
                    if run_play is not None:
                        if bool(not(re.search(r'B', run_play))) & bool(not(re.search(r'K', begin_play))):
                            this_line['1B_after'] = pid
                    else:
                        if bool(not(re.search(r'K', begin_play))):
                            this_line['1B_after'] = pid

                    # now process any base runners normally
                    this_line = br.base_running2(this_line, run_play, lineup, pid, hid)

                # Fielding Plays that are not FC
                elif bool(re.search(r'^[0-9]+', begin_play)):

                    # stats
                    st = ['AB', 'PA']
                    pt = ['IP', 'BF']

                    # DP or TP
                    if bool(re.search(r'(DP|TP)', begin_play)):
                        this_line['outs'] += 2

                        # batter is one of the outs
                        if not(re.search(r'\([123]\)([0-9]+)?\([123]\)', begin_play)):
                            # find out where the other out is
                            if re.search(r'\(1\)', begin_play):
                                gv.bases_after = 'XX' + gv.bases_after[1:]
                            elif re.search(r'\(2\)', begin_play):
                                gv.bases_after = 'X' + gv.bases_after[0:1] + 'X' + gv.bases_after[2]
                            else:
                                gv.bases_after = 'X' + gv.bases_after[:2] + 'X'
                        # batter is safe
                        else:
                            if bool(re.search(r'\(1\)', begin_play)) & bool(re.search(r'\(2\)', begin_play)):
                                gv.bases_after = 'BXX'
                            elif bool(re.search(r'\(1\)', begin_play)) & bool(re.search(r'\(3\)', begin_play)):
                                gv.bases_after = 'BX2'
                            else:
                                gv.bases_after = 'B1X'

                        if bool(re.search(r'TP', begin_play)):
                            this_line['outs'] += 3
                            gv.bases_after = '---'

                        if re.search('GDP', begin_play):
                            st.append('GDP')
                            pt.append('IDP')
                        sc.stat_collector(pid, lineup, this_line, st)
                        po.pitch_collector(pid, lineup, this_line, pt)

                        # now process any base runners normally
                        this_line = br.base_running2(this_line, run_play, lineup, pid, hid)

                    # check force out before normal outs
                    elif bool(re.search(r'^[0-9]+.*/FO', begin_play)):
                        this_line['outs'] += 1

                        # a runner is out
                        if re.search(r'\(B\)', begin_play):
                            gv.bases_after = 'X' + gv.bases_after
                        elif re.search(r'\(1\)', begin_play):
                            gv.bases_after = 'BX' + gv.bases_after[1:]
                            this_line['1B_after'] = pid
                        elif re.search(r'\(2\)', begin_play):
                            gv.bases_after = 'B' + gv.bases_after[0:1] + 'X' + gv.bases_after[2]
                            this_line['1B_after'] = pid
                        else:
                            gv.bases_after = 'B' + gv.bases_after[:2] + 'X'
                            this_line['1B_after'] = pid
                        sc.stat_collector(pid, lineup, this_line, st)
                        po.pitch_collector(pid, lineup, this_line, pt)

                        # now process any base runners normally
                        this_line = br.base_running2(this_line, run_play, lineup, pid, hid)

                    # normal out - NOT an error
                    elif bool(re.search(r'^[0-9]+(?!E)', begin_play)):
                        this_line['outs'] += 1

                        # batter is out
                        # using dash instead of X as this will hold runners unless run_play includes them
                        gv.bases_after = '-' + gv.bases_after
                        sc.stat_collector(pid, lineup, this_line, st)
                        po.pitch_collector(pid, lineup, this_line, pt)

                        # now process any base runners normally
                        this_line = br.base_running2(this_line, run_play, lineup, pid, hid)

            # # Case 1: regular single out plays - exclude SH/SF
            # if bool(re.search(r'^[1-9]([1-9!]+)?/(G|F|L|P|BG|BP|BL|IF)(?!/(SH|SF))', the_play)) | \
            #         bool(re.search(r'^[1-9]([1-9!]+)?$', the_play)):
            #     this_line['outs'] += 1
            #
            #     # stat add: AB, PA, LOB, RLSP
            #     st = ['AB', 'PA', 'LOB', 'RLSP']
            #     sc.stat_collector(pid, lineup, this_line, st)
            #
            #     # pitch add: IP, BF
            #     pt = ['IP', 'BF']
            #     po.pitch_collector(hid, lineup, this_line, pt)
            #
            # # Case 2: irregular put-outs, runner is specified
            # # i.e. when put out at base not normally covered by that fielder
            # elif re.search(r'^[1-9]([1-9]+)?\([B123]\)/(?!FO)', the_play):
            #     this_line['outs'] += 1
            #
            #     # determine which runner
            #     if re.search(r'^[1-9]([1-9]+)?\(B\)', the_play):
            #         # out is at 1B, no action required
            #         pass
            #     elif re.search(r'^[1-9]([1-9]+)?\([123]\)', the_play):
            #         # take a look
            #         print(the_game_id, ': ', the_play)
            #
            #     # stat add: AB, PA, LOB, RLSP
            #     st = ['AB', 'PA', 'LOB', 'RLSP']
            #     sc.stat_collector(pid, lineup, this_line, st)
            #
            #     # pitch add: IP, BF
            #     pt = ['IP', 'BF']
            #     po.pitch_collector(hid, lineup, this_line, pt)
            #
            # # Case 3: explicit force out plays
            # elif re.search(r'^[1-9]([1-9]+)?\([B123]\)/FO', the_play):
            #     this_line['outs'] += 1
            #
            #     # determine which runner
            #     if re.search(r'^[1-9]([1-9]+)?\(B\)', the_play):
            #         # mark an X for processing later.
            #         this_line['1B_after'] = 'X'
            #     elif re.search(r'^[1-9]([1-9]+)?\(1\)', the_play):
            #         # mark an X for processing later.
            #         this_line['2B_after'] = 'X'
            #     elif re.search(r'^[1-9]([1-9]+)?\(2\)', the_play):
            #         # mark an X for processing later.
            #         this_line['3B_after'] = 'X'
            #     elif re.search(r'^[1-9]([1-9]+)?\(3\)', the_play):
            #         # out at Home, no action required
            #         pass
            #
            #     # stat add: AB, PA, LOB, RLSP
            #     st = ['AB', 'PA', 'LOB', 'RLSP']
            #     sc.stat_collector(pid, lineup, this_line, st)
            #
            #     # pitch add: IP, BF
            #     pt = ['IP', 'BF']
            #     po.pitch_collector(hid, lineup, this_line, pt)
            #
            # # Case 4: sacrifice hit / fly
            # elif re.search(r'^[1-9]([1-9]+)?.*/(SH|SF)', the_play):
            #     this_line['outs'] += 1
            #
            #     # stat add: SH/SF, PA
            #     if re.search(r'SF', the_play):
            #         st = ['SF', 'PA']
            #     else:
            #         st = ['SH', 'PA']
            #     sc.stat_collector(pid, lineup, this_line, st)
            #
            #     # pitch add: IP, BF
            #     pt = ['IP', 'BF']
            #     po.pitch_collector(hid, lineup, this_line, pt)
            #
            # # Case 5: fielders' choice
            # elif re.search(r'^FC[1-9]', the_play):
            #     # determine if there was an out
            #     if re.search(r'[123]X[123H](?!\(([0-9]+)?E([0-9]+)?\))', the_play):
            #         this_line['outs'] += 1
            #
            #         # pitch add: IP, BF
            #         pt = ['IP', 'BF']
            #         po.pitch_collector(hid, lineup, this_line, pt)
            #
            #     # move batter if explicitly mentioned
            #     if re.search(r'B-2', the_play):
            #         this_line['2B_after'] = pid
            #     elif re.search(r'B-3', the_play):
            #         this_line['3B_after'] = pid
            #     elif re.search(r'B-H', the_play):
            #         this_line['runs_scored'] += 1
            #         st = ['R']
            #         sc.stat_collector(pid, lineup, this_line, st)
            #
            #     # batter is out and not a double play
            #     elif re.search(r'BX[123H]', the_play):
            #         if not(re.search(r'DP', the_play)):
            #             this_line['outs'] += 1
            #         else:
            #             # nothing happens here if double play
            #             # base_runner will handle both outs
            #             this_line['outs'] -= 1
            #     else:
            #         this_line['1B_after'] = pid
            #
            #     # stat add: AB, PA, LOB, RLSP
            #     st = ['AB', 'PA', 'LOB', 'RLSP']
            #     sc.stat_collector(pid, lineup, this_line, st)
            #
            # # Case 6: strike out with NO event
            # elif re.search(r'^K([1-9]+)?(?!\+)', the_play):
            #     this_line['outs'] += 1
            #
            #     # stat add: AB, K, PA, LOB, RLSP
            #     st = ['AB', 'K', 'PA', 'LOB', 'RLSP']
            #     sc.stat_collector(pid, lineup, this_line, st)
            #
            #     # pitch add: IP, BF, K
            #     pt = ['IP', 'BF', 'K']
            #     po.pitch_collector(hid, lineup, this_line, pt)
            #
            # # Case 7: strike out + event
            # elif re.search(r'^K\+', the_play):
            #     this_line['outs'] += 1
            #
            #     # pitch add: IP, BF, K
            #     pt = ['IP', 'BF', 'K']
            #
            #     # determine if next play is out or not.
            #     # determine which base stolen
            #     if re.search(r'SB', the_play):
            #         this_line = br.steal_processor(this_line, lineup)
            #
            #     # determine which base runner was caught
            #     elif re.search(r'CS', the_play):
            #         this_line['outs'] += 1
            #         this_line = br.steal_processor(this_line, lineup)
            #
            #     # if explicitly moves the batter on passed ball or WP
            #     elif re.search(r'(WP|PB)\..*B-[123H]', the_play):
            #         this_line['outs'] -= 1
            #         if re.search(r'\..*B-1', the_play):
            #             this_line['1B_after'] = pid
            #         elif re.search(r'\..*B-2', the_play):
            #             this_line['2B_after'] = pid
            #         elif re.search(r'\..*B-3', the_play):
            #             this_line['3B_after'] = pid
            #         elif re.search(r'\..*B-H', the_play):
            #             this_line['runs_scored'] = pid
            #
            #         # re-declare variable no more 'IP'
            #         pt = ['BF', 'K']
            #
            #     # otherwise PB that moves other runners or Defensive Indifference
            #     elif re.search(r'(WP|PB|DI)\.', the_play):
            #         # batter is still out -- i think
            #         if re.search(r'WP', the_play):
            #             pt.append('WP')
            #         elif re.search(r'PB', the_play):
            #             pt.append('PB')
            #         else:
            #             pt.append('DI')
            #
            #     # similar case for WP, no batter movement
            #     elif re.search(r'WP\..*[123]-[123H]', the_play):
            #         # batter is still out.
            #         pt.append('WP')
            #
            #     # Pick Off Error
            #     elif re.search(r'PO[123]\(([0-9]+)?E', the_play):
            #         # batter is still out.
            #         pt.append('POA')
            #
            #     # Pick Off DP
            #     elif re.search(r'PO[123].*/DP', the_play):
            #         # runner is also out
            #         this_line['outs'] += 1
            #         pt.extend(['IP', 'POA', 'PO'])
            #
            #         if re.search(r'PO1', the_play):
            #             this_line['1B_after'] = 'X'
            #         if re.search(r'PO2', the_play):
            #             this_line['2B_after'] = 'X'
            #         if re.search(r'PO3', the_play):
            #             this_line['3B_after'] = 'X'
            #
            #     # Other DP
            #     elif re.search(r'.*/DP', the_play):
            #         # a runner is also out
            #         # this_line['outs'] += 1 -- this is already recorded
            #         pt.append('IP')
            #
            #     # Error on Swing Striking 3
            #     elif re.search(r'K+E[0-9]', the_play):
            #         # let the base_runner function handle the rest.
            #         this_line['outs'] -= 1
            #
            #     # else
            #     else:
            #         # out applies anyway; no action required
            #         print('Game #: ', the_game_id, 'CHECK HERE: ', the_play)
            #
            #     # stat add: AB, K, PA, LOB, RLSP
            #     st = ['AB', 'K', 'PA', 'LOB', 'RLSP']
            #     sc.stat_collector(pid, lineup, this_line, st)
            #
            #     # pitcher stats add
            #     po.pitch_collector(hid, lineup, this_line, pt)
            #
            # # Case 8: routine double plays
            # elif re.search(r'.*DP', the_play):
            #     this_line['outs'] += 2
            #
            #     # determine which runners are out
            #     if re.search(r'\(1\)', the_play):
            #         this_line['2B_after'] = 'X'
            #     if re.search(r'\(2\)', the_play):
            #         this_line['3B_after'] = 'X'
            #     if re.search(r'\([123]\).*\([123]\)', the_play):
            #         # nothing happens if 3rd base runner is out.
            #         # both 1 and 2 would be recorded
            #         pass
            #     else:
            #         # record the out at 1st implicitly if only 1 other baserunner is out.
            #         this_line['1B_after'] = 'X'
            #
            #     # stat add: AB, PA, LOB, RLSP
            #     st = ['AB', 'PA', 'LOB', 'RLSP']
            #     sc.stat_collector(pid, lineup, this_line, st)
            #
            #     # pitch add: IP, IP, BF
            #     pt = ['IP', 'IP', 'BF']
            #     po.pitch_collector(hid, lineup, this_line, pt)
            #
            # # Case 9: triple plays
            # elif re.search(r'.*TP', the_play):
            #     this_line['outs'] += 3
            #
            #     # stat add: AB, PA, LOB, RLSP
            #     st = ['AB', 'PA', 'LOB', 'RLSP']
            #     sc.stat_collector(pid, lineup, this_line, st)
            #
            #     # pitch add: IP, IP, IP, BF
            #     pt = ['IP', 'IP', 'IP', 'BF']
            #     po.pitch_collector(hid, lineup, this_line, pt)
            #
            # # Case 10: catcher interference or pitcher/1B interference
            # elif re.search(r'^C/E[1-9]', the_play):
            #     this_line['1B_after'] = pid
            #
            #     # stat add: PA
            #     st = ['PA']
            #     sc.stat_collector(pid, lineup, this_line, st)
            #
            #     # pitch add: BF, CI
            #     pt = ['BF', 'CI']
            #     po.pitch_collector(hid, lineup, this_line, pt)
            #
            # # Case 11: hit! -- the fielder(s) after letter is optional; HIT + Errors are Resolved here too.
            # elif re.search(r'^((S|D|T)([1-9]+)?/?|H/|HR|DGR)', the_play):
            #
            #     # pitch add: BF, H
            #     pt = ['BF', 'H']
            #
            #     # determine what type of hit.
            #     if re.search(r'^S([1-9]+)?', the_play):
            #
            #         # stat add: AB, PA, H
            #         st = ['AB', 'PA', 'H']
            #
            #         # check if batter advanced elsewhere - e.g. Error on Throw / Catch
            #         if re.search(r'B-[23H]', the_play):
            #             if re.search(r'B-2', the_play):
            #                 this_line['2B_after'] = pid
            #             elif re.search(r'B-3', the_play):
            #                 this_line['3B_after'] = pid
            #             elif re.search(r'B-H', the_play):
            #                 this_line['runs_scored'] += 1
            #                 st.append('R')
            #                 pt.append('R')
            #         else:
            #             this_line['1B_after'] = pid
            #         sc.stat_collector(pid, lineup, this_line, st)
            #
            #     elif re.search(r'^(D([1-9]+)?|DGR)', the_play):
            #
            #         # stat add: AB, PA, H, D
            #         st = ['AB', 'PA', 'H', 'D']
            #         pt.append('D')
            #
            #         # check if batter advanced elsewhere
            #         if re.search(r'B-[3H]', the_play):
            #             if re.search(r'B-3', the_play):
            #                 this_line['3B_after'] = pid
            #             elif re.search(r'B-H', the_play):
            #                 this_line['runs_scored'] += 1
            #                 st.append('R')
            #                 pt.append('R')
            #         else:
            #             this_line['2B_after'] = pid
            #         sc.stat_collector(pid, lineup, this_line, st)
            #
            #     elif re.search(r'^T([1-9]+)?', the_play):
            #
            #         # stat add: AB, PA, H, T
            #         st = ['AB', 'PA', 'H', 'T']
            #         pt.append('T')
            #
            #         # check if batter advanced elsewhere
            #         if re.search(r'B-H', the_play):
            #             this_line['runs_scored'] += 1
            #             st.append('R')
            #             pt.append('R')
            #         else:
            #             this_line['3B_after'] = pid
            #         sc.stat_collector(pid, lineup, this_line, st)
            #
            #     else:
            #         this_line['runs_scored'] += 1
            #
            #         # stat add: AB, PA, H, HR, R
            #         st = ['AB', 'PA', 'H', 'HR', 'R']
            #         pt.extend(['HR', 'R'])
            #
            #         # score the RBI if not NR or NORBI
            #         if not (re.search(r'B-H\((NR|NORBI)\)', the_play)):
            #             st.append('RBI')
            #         if not (re.search(r'B-H([(NRORBI)]+)?\(UR\)', the_play)):
            #             pt.append('ER')
            #         sc.stat_collector(pid, lineup, this_line, st)
            #     po.pitch_collector(hid, lineup, this_line, pt)
            #
            # # Case 12: walk or hit by pitch
            # elif re.search(r'^(HP|IW|W(?!P))(?!\+)', the_play):
            #     # print('Walk / Hit By Pitch: ', the_play)
            #     this_line['1B_after'] = pid
            #
            #     # stat add: PA, W or HBP
            #     st = ['PA']
            #     # pitch add: BF
            #     pt = ['BF']
            #     if re.search(r'^HP', the_play):
            #         st.append('HBP')
            #         pt.append('HBP')
            #     elif re.search(r'^IW', the_play):
            #         st.extend(['IW', 'W'])
            #         pt.extend(['IBB', 'BB'])
            #     else:
            #         st.append('W')
            #         pt.append('BB')
            #     sc.stat_collector(pid, lineup, this_line, st)
            #     po.pitch_collector(hid, lineup, this_line, pt)
            #
            # # Case 13: walk + event
            # elif re.search(r'^(HP|IW|W(?!P))\+', the_play):
            #     # print('Walk + Event: ', the_play)
            #     this_line['1B_after'] = pid
            #
            #     # stat add: PA, W or HBP
            #     st = ['PA']
            #     # pitch add: BF
            #     pt = ['BF']
            #     if re.search(r'^HP', the_play):
            #         st.append('HBP')
            #         pt.append('HBP')
            #     elif re.search(r'^IW', the_play):
            #         st.extend(['IW', 'W'])
            #         pt.extend(['IBB', 'BB'])
            #     else:
            #         st.append('W')
            #         pt.append('BB')
            #     sc.stat_collector(pid, lineup, this_line, st)
            #     po.pitch_collector(hid, lineup, this_line, pt)
            #
            #     # DOES NOT DO ANYTHING ELSE!??!?! #
            #
            # # Case 14: error on FOUL fly ball
            # elif re.search(r'^FLE[1-9]', the_play):
            #     # print('FOUL Fly ball Error: ', the_play)
            #     pass
            #
            # # Case 15: error on ball in play
            # elif re.search(r'^([1-9]+)?E[1-9]', the_play):
            #     # print('Error: ', the_play)
            #
            #     # stat add: AB, PA
            #     st = ['AB', 'PA']
            #     # pitch add: BF
            #     pt = ['BF']
            #     # if explicitly puts moves the batter
            #     if re.search(r'\..*B(-|X)[123H]', the_play):
            #         if re.search(r'\..*B-1', the_play):
            #             this_line['1B_after'] = pid
            #         elif re.search(r'\..*B-2', the_play):
            #             this_line['2B_after'] = pid
            #         elif re.search(r'\..*B-3', the_play):
            #             this_line['3B_after'] = pid
            #         elif re.search(r'\..*B-H', the_play):
            #             this_line['runs_scored'] += 1
            #             # stat add: R
            #             st.append('R')
            #             pt.append('R')
            #             # score the RBI if not NR or NORBI
            #             if not(re.search(r'B-H\((NR|NORBI)\)', the_play)):
            #                 st.append('RBI')
            #             if not (re.search(r'B-H([(NRORBI)]+)?\(UR\)', the_play)):
            #                 pt.append('ER')
            #         # other cases are BX[123H] - base_runner function will handle.
            #     else:
            #         # assume they reached first base safely
            #         this_line['1B_after'] = pid
            #
            #     sc.stat_collector(pid, lineup, this_line, st)
            #     po.pitch_collector(hid, lineup, this_line, pt)
            #
            # # Case 16: wild pitch or balk
            # elif re.search(r'^(WP|BK)', the_play):
            #     if re.search(r'WP', the_play):
            #         pt = ['WP']
            #     else:
            #         pt = ['BK']
            #     po.pitch_collector(hid, lineup, this_line, pt)
            #
            # # Case 17: no pitch
            # elif re.search(r'^NP$', the_play):
            #     pass
            #
            # # Case 18: stolen base
            # elif re.search(r'^SB', the_play):
            #     # print('Stolen Base: ', the_play)
            #     this_line = br.steal_processor(this_line, lineup)
            #
            # # Case 19: defensive indifference
            # elif re.search(r'^DI', the_play):
            #     # pitch add: DI
            #     pt = ['DI']
            #     po.pitch_collector(hid, lineup, this_line, pt)
            #
            # # Case 20: caught stealing
            # elif re.search(r'^CS', the_play):
            #     # print('Caught Stealing: ', the_play)
            #     this_line['outs'] += 1
            #     this_line = br.steal_processor(this_line, lineup)
            #
            # # Case 21: pick off and/or caught stealing
            # elif re.search(r'^PO(CS)?[123H]', the_play):
            #     # print('Picked Off &/ Caught Stealing: ', the_play)
            #     if not(re.search(r'PO[123]\(([0-9]+)?E', the_play)):
            #         this_line['outs'] += 1
            #     this_line = br.steal_processor(this_line, lineup)
            #
            #     # pitch add:
            #     pt = ['POA', 'PO']
            #     po.pitch_collector(hid, lineup, this_line, pt)
            #
            # # Case 22: passed ball
            # elif re.search(r'^PB', the_play):
            #     # pitch add:
            #     pt = ['PB']
            #     po.pitch_collector(hid, lineup, this_line, pt)
            #
            # # Case 23: unexpected runner advance
            # elif re.search(r'^OA', the_play):
            #     # print('Unexpected Runner Adv.: ', the_play)
            #     pass
            #
            # # Case 24: batter interference
            # elif re.search(r'([1-9]+)/BINT', the_play):
            #     # print('Batter Interference: ', the_play)
            #     pass
            #
            # # Case 25: Hit with some errors
            # # Moved to HITS - Case #11
            #
            # # Case 26: appeal plays
            # elif re.search(r'.*AP', the_play):
            #     # print('Appeal Play not already overridden: ', the_play)
            #     pass
            #
            # # Case 20: ELSE
            # else:
            #     print('Game #: ', the_game_id, 'CASE NEEDED: ', the_play)
            #
            # # HANDLING BASERUNNERS
            # this_line = br.base_running(this_line, lineup, hid)

        # # this line item is substitution
        # else:
        #     this_line['1B_after'] = the_dict[i-1]['1B_before']
        #     this_line['2B_after'] = the_dict[i-1]['2B_before']
        #     this_line['3B_after'] = the_dict[i-1]['3B_before']
        #     # this_line['outs'] = the_dict[i-1]['outs']
        #     pid = this_line['playerID']
        #
        #     # if pinch-runner, put in the runner
        #     # batting team = the half inning
        #     if this_line['half'] == this_line['team_id']:
        #
        #         # pinch runner only
        #         if this_line['fielding'] == '12':
        #
        #             # check which spot in the lineup, get the playerID:
        #             sub_filter = (lineup.team_id == this_line['team_id']) & \
        #                          (lineup.bat_lineup == this_line['batting'])
        #             sub_index = lineup.index[sub_filter]
        #             sub_player_id = lineup.at[sub_index[0], 'player_id']
        #
        #             # check the bases for the runner:
        #             if this_line['1B_after'] == sub_player_id:
        #                 this_line['1B_after'] = pid
        #             elif this_line['2B_after'] == sub_player_id:
        #                 this_line['2B_after'] = pid
        #             elif this_line['3B_after'] == sub_player_id:
        #                 this_line['3B_after'] = pid
        #             else:
        #                 # most likely is Pinch Hitting -- make a check for this later; but should be '11'
        #                 pass
        #
        #             # replace the person in the lineup
        #             lineup.at[sub_index[0], 'player_id'] = pid
        #             lineup.at[sub_index[0], 'player_nm'] = this_line['name']
        #
        #             # add games played stat - as "batting" stat
        #             sc.stat_collector(pid, lineup, this_line, ['GP'])
        #
        #         # pinch hitter only
        #         elif this_line['fielding'] == '11':
        #
        #             # check which spot in the lineup, get the playerID:
        #             sub_filter = (lineup.team_id == this_line['team_id']) & \
        #                          (lineup.bat_lineup == this_line['batting'])
        #             sub_index = lineup.index[sub_filter]
        #
        #             # replace the person in the lineup
        #             lineup.at[sub_index[0], 'player_id'] = pid
        #             lineup.at[sub_index[0], 'player_nm'] = this_line['name']
        #
        #             # add games played stat - as "batting" stat
        #             sc.stat_collector(pid, lineup, this_line, ['GP'])
        #
        #     # fielding team = the half inning
        #     else:
        #         # check for only the pitching substitutions for now
        #         if this_line['fielding'] == '1':
        #             pitch_index = po.assign_pitcher(lineup, this_line, True)[1]
        #             lineup.at[pitch_index, 'player_id'] = this_line['playerID']
        #             lineup.at[pitch_index, 'player_nm'] = this_line['name']
        #
        #             # add games played stat - as "pitching" stat
        #             po.pitch_collector(pid, lineup, this_line, ['GP'])
        #
        # # do a check for > 3 outs
        # if this_line['outs'] > 3:
        #     print('BAD OUTS:', this_line['game_id'], '-', the_play, ' ', this_line['outs'])
        #
        # # performance checkpoint
        # q3_time = t.time()
        #
        # set the line back to the df to be stored properly.
        the_dict[i] = this_line
        # print(the_play, bases_before, this_line['1B_before'], this_line['2B_before'], this_line['3B_before'],
        #       this_line['outs'], this_line['1B_after'], this_line['2B_after'], this_line['3B_after'], gv.bases_after)
        #
        # # performance checkpoint
        # q4_time = t.time()
        #
        # # store to log
        # fgp = open('GAMEPLAY.LOG', mode='a')
        #
        # # performance review
        # fgp.write('LINE #' + str(i) + '\n')
        # fgp.write('setup: ' + str(q2_time - q1_time) + '\n')
        # fgp.write('play/sub: ' + str(q3_time - q2_time) + '\n')
        # fgp.write('reassign: ' + str(q4_time - q3_time) + '\n')
        # fgp.write('total: ' + str(q4_time - q1_time) + '\n')
        # fgp.close()

    return the_dict
