# libraries
import re
from . import stat_collector as sc
from . import global_variables as gv
from . import base_running as br
import time as t
from . import pitcher_oper as po
from . import non_plate_appearance as npa
from . import fielding_oper as fo
from . import error_logger as el
import numpy as np


# re-write the processor based on re.search/re.findall grep searching
# version 4 includes the processing_errors
def play_processor4(the_dict, games_roster, team_name, data_year):

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
                this_line['before_1B'] = the_dict[i-1]['after_1B']
                this_line['before_2B'] = the_dict[i-1]['after_2B']
                this_line['before_3B'] = the_dict[i-1]['after_3B']
                this_line['outs'] = the_dict[i-1]['outs']
            else:
                # see if pass works
                pass

        # performance checkpoint
        q2_time = t.time()

        # for plays
        if this_line['gm_type'] == 'play':

            # take out any ! in play
            this_line['play'] = this_line['play'].replace('!', '')

            # assign the pitcher - UNLESS NP

            this_line['pitcherID'] = po.assign_pitcher(lineup, this_line)

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

                # base_runner movements
                if run_play is not None:
                    this_line = br.base_running2(this_line, run_play, lineup, pid, hid)

                # handle defensive errors for non-PA plays


            # plate-appearance play
            else:

                # if it is a HIT
                if bool(re.search(r'^((S|D|T)([1-9]+)?/?|H/|HR|DGR)', begin_play)):

                    # if not error. if explicit batter movement, don't perform batter movement
                    if not(bool(re.search(r'E[0-9]+', begin_play))):

                        batter_move = bool(re.search('B(-|X)[123H]', this_line['play']))

                        # stats
                        st = ['AB', 'PA', 'H']
                        pt = ['BF', 'H']

                        # single
                        if re.search(r'^S', begin_play) and not batter_move:
                            this_line['after_1B'] = pid
                            gv.bases_after = 'B' + gv.bases_after
                        # double
                        elif re.search(r'^D', begin_play):
                            if not batter_move:
                                this_line['after_2B'] = pid
                                gv.bases_after = '0B' + gv.bases_after
                            st.append('D')
                            pt.append('D')
                        # triple
                        elif re.search(r'^T', begin_play):
                            if not batter_move:
                                this_line['after_3B'] = pid
                                gv.bases_after = '00B' + gv.bases_after
                            st.append('T')
                            pt.append('T')
                        # home run
                        else:
                            if not batter_move:
                                this_line['runs_scored'] += 1
                                gv.bases_after = '---'
                                st.extend(['HR', 'R', 'RBI'])
                                pt.extend(['HR', 'R', 'ER'])

                        # stat process
                        sc.stat_collector(pid, lineup, this_line, st)
                        po.pitch_collector(hid, lineup, this_line, pt)

                        # base_runner movements, including batter moves
                        this_line = br.base_running2(this_line, run_play, lineup, pid, hid)

                    else:
                        print('Hit + Error on batter:', begin_play, '==', run_play)
                        el.processing_errors('Hit + Error on batter: ' + begin_play + ' == ' + run_play,
                                             'play_processor', team_name, data_year,
                                             the_game_id, this_line['half_innings'])

                # Walk or Strikeout
                elif bool(re.search(r'^(IW|HP|W|K)', begin_play)):

                    # handle these scenarios normally
                    if bool(re.search(r'K', begin_play)):
                        this_line['outs'] += 1
                        gv.bases_after = '-' + gv.bases_after

                        st = ['AB', 'PA', 'K', 'LOB', 'RLSP']
                        sc.stat_collector(pid, lineup, this_line, st)
                        pt = ['IP', 'BF', 'K']
                        po.pitch_collector(hid, lineup, this_line, pt)

                        # handle defensive throws
                        if bool(re.search(r'K[1-9]+', begin_play)):
                            k_play = re.sub(r'K([1-9]+).*', '\\1', begin_play)
                            fo.fielding_assign_stats(r'', k_play, lineup, this_line, ['A'], ['PO'])

                    elif bool(re.search(r'HP', begin_play)):
                        gv.bases_after = 'B' + gv.bases_after

                        st = ['PA', 'HBP']
                        sc.stat_collector(pid, lineup, this_line, st)
                        pt = ['BF', 'HBP']
                        po.pitch_collector(hid, lineup, this_line, pt)

                    else:
                        gv.bases_after = 'B' + gv.bases_after

                        st = ['PA', 'W']
                        pt = ['BF', 'BB']
                        if bool(re.search(r'^IW', begin_play)):
                            st.append('IW')
                            pt.append('IBB')
                        sc.stat_collector(pid, lineup, this_line, st)
                        po.pitch_collector(hid, lineup, this_line, pt)

                    # check if additional event happened
                    if bool(re.search(r'\+', begin_play)):

                        # run the NON-PA function
                        this_line = npa.non_pa(this_line, begin_play, run_play, lineup, pid, hid)

                        # K+CS/DP Case
                        if bool(re.search(r'^K\+.*(DP|TP)', begin_play)):

                            # for CS, the base_running will handle the assists and putouts
                            # only take care of the DP/TP here
                            if not(bool(re.search(r'NDP', begin_play))) and bool(re.search(r'CS|PO', begin_play)):
                                fielders = re.sub(r'.*(CS|PO)[123H]\(([1-9]+)\).*', '\\2', begin_play)
                                for idx in range(0, len(fielders)):
                                    if bool(re.search(r'DP', begin_play)):
                                        ft = ['DP']
                                    else:
                                        ft = ['TP']
                                    fo.fielding_processor(fielders[idx], lineup, this_line, ft)
                            else:
                                if not(bool(re.search(r'NDP', begin_play))):
                                    print('Not CS or PO case', this_line['play'])

                    # if no batter movements, then put batter on first!
                    if run_play is not None:
                        if not(bool(re.search(r'B', run_play))) and not(bool(re.search(r'K', begin_play))):
                            this_line['after_1B'] = pid
                        elif bool(re.search('K.*B-', this_line['play'])) and not(bool(re.search('\+', begin_play))):
                            this_line['outs'] -= 1
                            # let base_runner function handle this.
                    else:
                        if not(bool(re.search(r'K', begin_play))):
                            this_line['after_1B'] = pid
                    # the K+WP.B-1 or K+PB.B-1 scenarios - runner is moved by below.

                    # now process any base runners normally
                    this_line = br.base_running2(this_line, run_play, lineup, pid, hid)

                # Fielding Plays that are not FC
                elif bool(re.search(r'^([0-9]+)?E?[0-9]+', begin_play)):

                    # stats
                    st = ['AB', 'PA']
                    pt = ['IP', 'BF']

                    # DP or TP -- exclude NDPs, so political
                    if bool(re.search(r'(DP|TP)', begin_play)) and not(bool(re.search(r'NDP', begin_play))):
                        this_line['outs'] += 2

                        '''
                        - Handle the batter -- out or advance; move runner(s); apply assist(s) and put out
                        - Manage the baserunner outs -- as double play / triple play
                        - Manage the force-out runners -- out or advance
                        - Do not double-assign assists for baserunner + force-outs
                        '''
                        #  -----  BATTER IS OUT!  -----  #
                        check_batter = [p for p in re.sub(r'/.*', '', begin_play)]
                        if (check_batter[len(check_batter) - 1].isdigit()) or (bool(re.search(r'\(B\)', begin_play))):

                            # since batter is out, last fielder is putout, everyone else is assist
                            # unless otherwise specified - e.g. 43(B)6(1)/GDP
                            if bool(re.search(r'\(B\)', begin_play)):
                                # assign the batter put out
                                double_play = re.sub(r'\([123]\)', '', begin_play)
                                fo.fielding_po(double_play, r'\(B\).*', lineup, this_line)  # record PO

                                # assists assigned later
                            else:
                                fielders = fo.fielding_unique(r'\([\d]+\)|\D', begin_play)
                                # record a putout for last fielder
                                idx = len(fielders) - 1
                                ft = ['PO']
                                fo.fielding_processor(fielders[idx], lineup, this_line, ft)

                                # assists assigned later

                            # assign the batter as OUT
                            gv.bases_after = 'X' + gv.bases_after[0:]

                        #  -----  BATTER IS SAFE  -----  #
                        else:
                            # assign the batter as SAFE
                            gv.bases_after = 'B' + gv.bases_after[0:]
                        #  ----------------------------  #

                        #  -----  MANAGE RUNNERS  -----  #
                        runner_out_play = re.sub(r'.*\.', '', this_line['play'])
                        check_runner_out = False

                        # check for runner-out play, include RINT; skip Errors (as runner is then safe)
                        if bool(re.search(r'.*[B123]X[123H]\([1-9/RINT]+\).*', runner_out_play)):

                            # the actual runner_out play will be handled in base_running
                            check_runner_out = True

                        #  ----------------------------  #

                        #  -----  HANDLE FORCE OUTS  -----  #
                        force_out_play = re.sub(r'\(B\)', '', begin_play)
                        check_force_out = False

                        # check (1), 1B runner is forced out
                        if re.search(r'\(1\)', force_out_play):
                            temp_play = re.sub(r'\([23]\)', '', force_out_play)
                            gv.bases_after = gv.bases_after[0:1] + 'X' + gv.bases_after[2:]
                            fo.fielding_po(temp_play, r'\(1\).*', lineup, this_line)  # record PO
                            check_force_out = True

                        # check (2), 2B runner is forced out
                        if re.search(r'\(2\)', force_out_play):
                            temp_play = re.sub(r'\([13]\)', '', force_out_play)
                            gv.bases_after = gv.bases_after[0:2] + 'X' + gv.bases_after[3:]
                            fo.fielding_po(temp_play, r'\(2\).*', lineup, this_line)  # record PO
                            check_force_out = True

                        # check (3), 3B runner is forced out
                        if re.search(r'\(3\)', force_out_play):
                            temp_play = re.sub(r'\([12]\)', '', force_out_play)
                            gv.bases_after = gv.bases_after[0:3] + 'X'
                            fo.fielding_po(temp_play, r'\(3\).*', lineup, this_line)  # record PO
                            check_force_out = True

                        # Case 1: Force Out + Runner Out
                        if check_force_out and check_runner_out:

                            # --- RUNNER OUT SCENARIO --- #
                            # first-out-only assists -- The Force Out Fielders
                            fielders = fo.fielding_unique(r'\([\dB]+\)|\D', begin_play)
                            for idx in range(0, len(fielders)):
                                if idx < len(fielders) - 1:
                                    # record an assist for this fielder
                                    ft = ['A']
                                    fo.fielding_processor(fielders[idx], lineup, this_line, ft)

                            # fielder contributing to baserunner-outs-only DPs (assist/putout in base_running)
                            runner = re.sub(r'.*([B123]X[123H]\([1-9]+\)).*', '\\1',
                                            re.sub(r'.*\.', '', this_line['play']))
                            second_out = fo.fielding_unique(r'.*\(|\D', runner)
                            mark_dp = list(np.setdiff1d(second_out, fielders))
                            for idx in range(0, len(mark_dp)):
                                if bool(re.search(r'DP', begin_play)):
                                    ft = ['DP']
                                else:
                                    ft = ['TP']
                                fo.fielding_processor(mark_dp[idx], lineup, this_line, ft)

                        # Case 2: Force Outs; No Runner Outs
                        elif check_force_out and (not check_runner_out):

                            # grab all but last fielder if batter was out, then run unique
                            if bool(re.search(r'([1-9])/.*', begin_play)):
                                case_two = re.sub(r'([1-9])/.*', '', begin_play)
                            else:
                                case_two = re.sub(r'/.*', '', begin_play)
                            fielders = fo.fielding_unique(r'\([\dB]+\)|\D', case_two)
                            for idx in range(0, len(fielders)):
                                if idx < len(fielders) - 1:
                                    # record Assist for not-last fielder
                                    ft = ['A']
                                    fo.fielding_processor(fielders[idx], lineup, this_line, ft)

                        # Case 3: Only 1 Force Out; and Runner is out:
                        elif (not check_force_out) and check_runner_out:

                            # fielder contributing to baserunner-outs-only DPs (assist/putout in base_running)
                            fielders = fo.fielding_unique(r'\([\dB]+\)|\D', begin_play)
                            runner = re.sub(r'.*([B123]X[123H]\([1-9]+\)).*', '\\1',
                                            re.sub(r'.*\.', '', this_line['play']))
                            second_out = fo.fielding_unique(r'.*\(|\D', runner)
                            mark_dp = list(np.setdiff1d(second_out, fielders))
                            for idx in range(0, len(mark_dp)):
                                if bool(re.search(r'DP', begin_play)):
                                    ft = ['DP']
                                else:
                                    ft = ['TP']
                                fo.fielding_processor(mark_dp[idx], lineup, this_line, ft)

                        # Case 4??
                        else:
                            print('UNKNOWN DP/TP Case:', this_line['play'], check_force_out, check_runner_out)
                            print(begin_play, bool(re.search(r'.*[B123]X[123H]\([1-9/RINT]+\).*', runner_out_play)))
                        #  -------------------------------  #

                        # record the TP stat
                        if bool(re.search(r'TP', begin_play)):
                            this_line['outs'] += 1
                            gv.bases_after = '---'

                            # check if batter was one of the 3 outs
                            check_batter = [p for p in re.sub(r'/.*', '', begin_play)]
                            if check_batter[len(check_batter)-1].isdigit():
                                fo.fielding_po(begin_play, r'/.*', lineup, this_line)  # record PO
                            else:
                                print(begin_play, the_game_id, this_line['play'])
                        # record the DP stat
                        else:
                            fielders = fo.fielding_unique(r'\([\dB]+\)|\D', begin_play)
                            ft = ['DP']
                            for idx in range(0, len(fielders)):
                                fo.fielding_processor(fielders[idx], lineup, this_line, ft)

                        if re.search('GDP', begin_play):
                            st.append('GDP')
                            pt.append('IDP')

                    # check force out before normal outs
                    elif bool(re.search(r'^[0-9]+.*/FO', begin_play)):
                        this_line['outs'] += 1

                        # a runner is out
                        if re.search(r'\(B\)', begin_play):
                            gv.bases_after = 'X' + gv.bases_after
                            fo.fielding_po(begin_play, r'\(B\).*', lineup, this_line)  # record PO

                        elif re.search(r'\(1\)', begin_play):
                            gv.bases_after = 'BX' + gv.bases_after[1:]
                            this_line['after_1B'] = pid
                            fo.fielding_po(begin_play, r'\(1\).*', lineup, this_line)  # record PO

                        elif re.search(r'\(2\)', begin_play):
                            gv.bases_after = 'B' + gv.bases_after[0:1] + 'X' + gv.bases_after[2]
                            this_line['after_1B'] = pid
                            fo.fielding_po(begin_play, r'\(2\).*', lineup, this_line)  # record PO

                        else:
                            gv.bases_after = 'B' + gv.bases_after[:2] + 'X'
                            this_line['after_1B'] = pid
                            fo.fielding_po(begin_play, r'\(3\).*', lineup, this_line)  # record PO

                        # assign assists
                        fielders = fo.fielding_unique(r'\([\dB]+\)|\D', begin_play)
                        for idx in range(0, len(fielders)):
                            if idx < len(fielders) - 1:
                                # record Assist for not-last fielder
                                ft = ['A']
                                fo.fielding_processor(fielders[idx], lineup, this_line, ft)

                    # fielding error
                    elif bool(re.search(r'^([0-9]+)?E', begin_play)):
                        # batter is safe - unless specified in run_play
                        gv.bases_after = 'B' + gv.bases_after
                        st.append('ROE')  # reached on error
                        pt = ['BF']

                        # assign assists and errors
                        fo.fielding_assign_stats(r'E|\D', begin_play, lineup, this_line, ['A'], ['E'])

                    # normal out -- this should be last to handle all cases prior
                    elif bool(re.search(r'^[0-9]+', begin_play)):
                        this_line['outs'] += 1

                        # this case might come back: 54(B)/BG25/SH.1-2
                        # putout by fielder not normally covering that base

                        # batter is out
                        # using dash instead of X as this will hold runners unless run_play includes them
                        gv.bases_after = '-' + gv.bases_after

                        # record assist(s) and put out
                        normal_out = re.sub('/.*', '', begin_play)
                        fo.fielding_assign_stats(r'\D', normal_out, lineup, this_line, ['A'], ['PO'])

                    # fielding plays that are not included above
                    else:
                        print('Fielding Plays not included: ', begin_play)
                        el.processing_errors('Fielding Plays not included: ' + begin_play,
                                             'play_processor', team_name, data_year,
                                             the_game_id, this_line['half_innings'])

                    # record any SH/SF otherwise, all are LOB/RLSP if not an error
                    if bool(re.search(r'SH', begin_play)):
                        st.append('SH')
                    elif bool(re.search(r'SF', begin_play)):
                        st.append('SF')
                    elif not(bool(re.search(r'E', begin_play))):
                        st.extend(['LOB', 'RLSP'])
                    sc.stat_collector(pid, lineup, this_line, st)
                    po.pitch_collector(hid, lineup, this_line, pt)

                    # now process any base runners normally
                    this_line = br.base_running2(this_line, run_play, lineup, pid, hid)

                # Fielder's Choice
                elif bool(re.search(r'^FC', begin_play)):

                    # DPs are handled by the runner marked out.
                    # this_line['outs'] += 1
                    st = ['AB', 'PA']
                    pt = ['BF']

                    # determine if anyone is out
                    if bool(re.search(r'[B123]X[23H]', this_line['play'])) and \
                            not(bool(re.search(r'[B123]X[23H]\([1-9]?E[1-9]+', this_line['play']))):
                        # this is handled in the base-running section
                        pass
                    else:
                        # everyone is safe; move batter unless explicit
                        if bool(re.search(r'B(-|X)[123H]', this_line['play'])):
                            # print("Explicit Batter - FC", this_line['play'])
                            # base-running section will move the batter accordingly
                            pass
                        else:
                            gv.bases_after = 'B' + gv.bases_after

                    sc.stat_collector(pid, lineup, this_line, st)
                    po.pitch_collector(hid, lineup, this_line, pt)

                    # now process any base runners normally
                    this_line = br.base_running2(this_line, run_play, lineup, pid, hid)

                # Catcher Interference
                elif bool(re.search(r'C/E[1-3]', begin_play)):
                    st = ['PA']
                    pt = ['BF', 'CI']
                    this_line['after_1B'] = pid
                    sc.stat_collector(pid, lineup, this_line, st)
                    po.pitch_collector(hid, lineup, this_line, pt)

                    # now process any base runners normally
                    this_line = br.base_running2(this_line, run_play, lineup, pid, hid)

                # find other plays:
                else:
                    print('Category Needed: ', begin_play)
                    el.processing_errors('Category Needed: ' + begin_play,
                                         'play_processor', team_name, data_year,
                                         the_game_id, this_line['half_innings'])

                # record pitcher stats
                po.pitch_count_collector(hid, pid, lineup, this_line)

        # this line item is substitution
        else:
            this_line['after_1B'] = the_dict[i-1]['before_1B']
            this_line['after_2B'] = the_dict[i-1]['before_2B']
            this_line['after_3B'] = the_dict[i-1]['before_3B']
            this_line['inning'] = the_dict[i-1]['inning']
            this_line['half'] = the_dict[i-1]['half']
            this_line['half_innings'] = the_dict[i-1]['half_innings']
            pid = this_line['playerID']

            # if pinch-runner, put in the runner
            # batting team = the half inning
            if this_line['half'] == this_line['team_id']:

                # pinch runner only
                if this_line['fielding'] == '12':

                    # update the lineup for this person
                    substitution = fo.lineup_substitution(this_line, lineup, pid, 'batting', '12')
                    lineup = substitution[0]
                    sub_player_id = lineup.at[substitution[1][0], 'player_id']

                    # check the bases for the runner:
                    if this_line['after_1B'] == sub_player_id:
                        this_line['after_1B'] = pid
                    elif this_line['after_2B'] == sub_player_id:
                        this_line['after_2B'] = pid
                    elif this_line['after_3B'] == sub_player_id:
                        this_line['after_3B'] = pid
                    else:
                        # most likely is Pinch Hitting -- make a check for this later; but should be '11'
                        pass

                    # add games played stat - as "batting" stat
                    sc.stat_collector(pid, lineup, this_line, ['GP'])

                # pinch hitter only
                elif this_line['fielding'] == '11':

                    # update the lineup for this person
                    substitution = fo.lineup_substitution(this_line, lineup, pid, 'batting', '11')
                    lineup = substitution[0]

                    # add games played stat - as "batting" stat
                    sc.stat_collector(pid, lineup, this_line, ['GP'])

                # what other scenarios here?
                else:
                    print(this_line['half_innings'], this_line['team_id'],
                          this_line['playerID'], this_line['batting'], this_line['fielding'])
                    el.processing_errors('Missing Substitution Scenario: ' + this_line['half_innings'] +
                                         this_line['team_id'] + this_line['playerID'] + this_line['batting'] +
                                         this_line['fielding'],
                                         'play_processor', team_name, data_year,
                                         the_game_id, this_line['half_innings'])

            # fielding team = the half inning
            else:
                # pitching substitution
                if this_line['fielding'] == '1':
                    # update the lineup for this pitcher
                    substitution = fo.lineup_substitution(this_line, lineup, pid, 'pitching', this_line['fielding'])
                    lineup = substitution[0]

                    # add games played stat - as "pitching" stat
                    po.pitch_collector(pid, lineup, this_line, ['GP'])

                # other fielding substitutions
                else:
                    # update the lineup for this person
                    substitution = fo.lineup_substitution(this_line, lineup, pid, 'fielding', this_line['fielding'])
                    lineup = substitution[0]

                    # add games played stat - as "batting" stat
                    if substitution[2]:
                        sc.stat_collector(pid, lineup, this_line, ['GP'])

        # do a check for > 3 outs
        '''
        if this_line['outs'] > 3:
            print('BAD OUTS:', this_line['game_id'], '-', the_play, ' ', this_line['outs'])
            el.processing_errors('BAD OUTS:' + str(the_play) + ' ' + str(this_line['outs']),
                                 'play_processor', team_name, data_year,
                                 the_game_id, this_line['half_innings'])
        '''
        #
        # # performance checkpoint
        # q3_time = t.time()
        #
        # set the line back to the df to be stored properly.
        the_dict[i] = this_line
        # print(the_play, bases_before, this_line['before_1B'], this_line['before_2B'], this_line['before_3B'],
        #       this_line['outs'], this_line['after_1B'], this_line['after_2B'], this_line['after_3B'], gv.bases_after)
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
