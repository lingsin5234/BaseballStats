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
                            this_line['after_1B'] = pid
                            gv.bases_after = 'B' + gv.bases_after
                        # double
                        elif re.search(r'^D', begin_play):
                            this_line['after_2B'] = pid
                            gv.bases_after = '0B' + gv.bases_after
                            st.append('D')
                            pt.append('D')
                        # triple
                        elif re.search(r'^T', begin_play):
                            this_line['after_3B'] = pid
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

                    # if no batter movements, then put batter on first!
                    if run_play is not None:
                        if bool(not(re.search(r'B', run_play))) & bool(not(re.search(r'K', begin_play))):
                            this_line['after_1B'] = pid
                        elif bool(re.search('K.*B-', this_line['play'])) & bool(not(re.search('\+', begin_play))):
                            this_line['outs'] -= 1
                            # let base_runner function handle this.
                    else:
                        if bool(not(re.search(r'K', begin_play))):
                            this_line['after_1B'] = pid
                    # the K+WP.B-1 or K+PB.B-1 scenarios - runner is moved by below.

                    # now process any base runners normally
                    this_line = br.base_running2(this_line, run_play, lineup, pid, hid)

                # Fielding Plays that are not FC
                elif bool(re.search(r'^([0-9]+)?E?[0-9]+', begin_play)):

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
                            elif re.search(r'\(3\)', begin_play):
                                gv.bases_after = 'X' + gv.bases_after[:2] + 'X'
                            else:
                                # baserunners will resolve last out (e.g. doubled up)
                                gv.bases_after = 'X' + gv.bases_after
                                this_line['outs'] -= 1

                            # since batter is out, last fielder is putout, everyone else is assist
                            fielders = [int(f) for f in re.sub(r'\([\d]+\)|\D', '', begin_play)]
                            for idx in range(0, len(fielders)):
                                if idx < len(fielders)-1:
                                    # record an assist & DP for this fielder
                                    ft = ['A', 'DP']
                                    fo.fielding_processor(fielders[idx], lineup, this_line, ft)
                                else:
                                    # record a putout & DP for this fielder
                                    ft = ['PO', 'DP']
                                    fo.fielding_processor(fielders[idx], lineup, this_line, ft)

                        # batter is safe
                        else:
                            if bool(re.search(r'\(1\)', begin_play)) & bool(re.search(r'\(2\)', begin_play)):
                                gv.bases_after = 'BXX'
                            elif bool(re.search(r'\(1\)', begin_play)) & bool(re.search(r'\(3\)', begin_play)):
                                gv.bases_after = 'BX2'
                            else:
                                gv.bases_after = 'B1X'

                        if bool(re.search(r'TP', begin_play)):
                            this_line['outs'] += 1
                            gv.bases_after = '---'

                        if re.search('GDP', begin_play):
                            st.append('GDP')
                            pt.append('IDP')

                    # check force out before normal outs
                    elif bool(re.search(r'^[0-9]+.*/FO', begin_play)):
                        this_line['outs'] += 1

                        # a runner is out
                        if re.search(r'\(B\)', begin_play):
                            gv.bases_after = 'X' + gv.bases_after
                        elif re.search(r'\(1\)', begin_play):
                            gv.bases_after = 'BX' + gv.bases_after[1:]
                            this_line['after_1B'] = pid
                        elif re.search(r'\(2\)', begin_play):
                            gv.bases_after = 'B' + gv.bases_after[0:1] + 'X' + gv.bases_after[2]
                            this_line['after_1B'] = pid
                        else:
                            gv.bases_after = 'B' + gv.bases_after[:2] + 'X'
                            this_line['after_1B'] = pid

                    # fielding error
                    elif bool(re.search(r'^([0-9]+)?E', begin_play)):
                        # batter is safe - unless specified in run_play
                        gv.bases_after = 'B' + gv.bases_after
                        st.append('ROE')  # reached on error
                        pt = ['BF']

                    # normal out -- this should be last to handle all cases prior
                    elif bool(re.search(r'^[0-9]+', begin_play)):
                        this_line['outs'] += 1

                        # this case might come back: 54(B)/BG25/SH.1-2
                        # putout by fielder not normally covering that base

                        # batter is out
                        # using dash instead of X as this will hold runners unless run_play includes them
                        gv.bases_after = '-' + gv.bases_after

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
                    elif bool(not(re.search(r'E', begin_play))):
                        st.extend(['LOB', 'RLSP'])
                    sc.stat_collector(pid, lineup, this_line, st)
                    po.pitch_collector(hid, lineup, this_line, pt)

                    # now process any base runners normally
                    this_line = br.base_running2(this_line, run_play, lineup, pid, hid)

                # Fielder's Choice
                elif bool(re.search(r'^FC', begin_play)):
                    # DPs are handled by the runner marked out.
                    this_line['outs'] += 1
                    st = ['AB', 'PA']
                    pt = ['IP', 'BF']

                    # determine who is out
                    if re.search(r'\(B\)', begin_play):
                        gv.bases_after = 'X' + gv.bases_after
                        st.append('LOB', 'RLSP')
                    elif re.search(r'\(1\)', begin_play):
                        gv.bases_after = 'BX' + gv.bases_after[1:]
                        this_line['after_1B'] = pid
                        st.append('LOB', 'RLSP')
                    elif re.search(r'\(2\)', begin_play):
                        gv.bases_after = 'B' + gv.bases_after[0:1] + 'X' + gv.bases_after[2]
                        this_line['after_1B'] = pid
                        st.append('LOB', 'RLSP')
                    elif re.search(r'\(3\)', begin_play):
                        gv.bases_after = 'B' + gv.bases_after[:2] + 'X'
                        this_line['after_1B'] = pid
                        st.append('LOB', 'RLSP')
                    else:
                        # NO ONE IS OUT
                        gv.bases_after = 'B' + gv.bases_after
                        this_line['outs'] -= 1
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
        if this_line['outs'] > 3:
            print('BAD OUTS:', this_line['game_id'], '-', the_play, ' ', this_line['outs'])
            el.processing_errors('BAD OUTS:' + str(the_play) + ' ' + str(this_line['outs']),
                                 'play_processor', team_name, data_year,
                                 the_game_id, this_line['half_innings'])
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
