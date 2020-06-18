# tracking base running movement
# libraries
import re
from . import stat_collector as sc
from . import global_variables as gv
from . import pitcher_oper as po
from . import fielding_oper as fo


# stolen base tracking
def steal_processor(this_line, lineup):

    # check if steal, then which base(s)
    if re.search(r'SB', this_line['play']):

        # SBH is listed first for double steal
        if re.search(r'SBH', this_line['play']):
            # if NOT an error on throwing
            if not (re.search(r'SBH.3-[H]\(([0-9]+)?E([0-9]+)?', this_line['play'])):
                this_line['runs_scored'] += 1
                gv.bases_after = gv.bases_after.replace('3', 'R')

            # stat add: SB, R
            st = ['SB', 'R']
            sc.stat_collector(this_line['before_3B'], lineup, this_line, st)

        # SB3 is listed next for double steal
        if re.search(r'SB3', this_line['play']):
            # if NOT an error on throwing
            if not (re.search(r'SB3.2-[3H]\(([0-9]+)?E([0-9]+)?', this_line['play'])):
                this_line['after_3B'] = this_line['before_2B']
                gv.bases_after = gv.bases_after[:len(gv.bases_after)-2] + '-2'
                # if there was a runner after, he would've went home/out at home
                # otherwise, no need to move the - ; e.g. -2- becomes --2- on steal of 3B

            # stat add: SB
            st = ['SB']
            sc.stat_collector(this_line['before_2B'], lineup, this_line, st)

        # SB2 is listed last on steals
        if re.search(r'SB2', this_line['play']):
            # if NOT an error on throwing
            if not(re.search(r'SB2.1-[23H]\(([0-9]+)?E([0-9]+)?', this_line['play'])):
                this_line['after_2B'] = this_line['before_1B']
                # if next base is '-' that means no one at 2B previously
                if bool(re.search(r'^1-', gv.bases_after)):
                    gv.bases_after = '-1' + gv.bases_after[len(gv.bases_after) - 1:]
                else:
                    # otherwise shift value over, could be double steal
                    gv.bases_after = '-1' + gv.bases_after[len(gv.bases_after) - 2:]

            # stat add: SB
            st = ['SB']
            sc.stat_collector(this_line['before_1B'], lineup, this_line, st)

    # check if caught stealing, then which base(s); but NO ERROR for this particular CS
    if bool(re.search(r'CS', this_line['play'])) and \
            not(bool(re.search(r'CS[23H]\([1-9]?E[1-9/TH]+\)', this_line['play']))):
        if re.search(r'CS2', this_line['play']):
            gv.bases_after = gv.bases_after.replace('1', 'X')
            # stat add: CS
            st = ['CS']
            sc.stat_collector(this_line['before_1B'], lineup, this_line, st)

            # fielding assist and putout
            cs_play = re.sub(r'.*CS2\(([1-9]+)\).*', '\\1', this_line['play'])
            fo.fielding_assign_stats(r'\D', cs_play, lineup, this_line, ['A'], ['PO'])

        if re.search(r'CS3', this_line['play']):
            gv.bases_after = gv.bases_after.replace('2', 'X')
            # stat add: CS
            st = ['CS']
            sc.stat_collector(this_line['before_2B'], lineup, this_line, st)

            # fielding assist and putout
            cs_play = re.sub(r'.*CS3\(([1-9]+)\).*', '\\1', this_line['play'])
            fo.fielding_assign_stats(r'\D', cs_play, lineup, this_line, ['A'], ['PO'])

        if re.search(r'CSH', this_line['play']):
            gv.bases_after = gv.bases_after.replace('3', 'X')
            # stat add: CS
            st = ['CS']
            sc.stat_collector(this_line['before_3B'], lineup, this_line, st)

            # fielding assist and putout
            cs_play = re.sub(r'.*CSH\(([1-9]+)\).*', '\\1', this_line['play'])
            fo.fielding_assign_stats(r'\D', cs_play, lineup, this_line, ['A'], ['PO'])

        # caught double steal DP
        if re.search(r'CS.*CS.*DP', this_line['play']):
            print('CAUGHT DOUBLE STEAL!!', this_line['play'])

            # fielding assist and putout
            steal1, steal2 = re.sub(r'.*CSH\(([1-9]+)\).*CSH\(([1-9]+)\).*', '\\1-\\2', this_line['play']).split('-')
            fo.fielding_assign_stats(r'.*\(|\D', steal1, lineup, this_line, ['A'], ['PO'])
            fo.fielding_assign_stats(r'.*\(|\D', steal2, lineup, this_line, ['A'], ['PO'])

    # else if caught stealing but error
    elif bool(re.search(r'CS', this_line['play'])) and \
            bool(re.search(r'CS[23H]\([1-9]?E[1-9/TH]+\)', this_line['play'])):

        # the runner advance will be handled separately just need to handle the fielding here
        play_in_question = re.sub(r'.*CS[23H]\(([1-9E]+)\).*', '\\1', this_line['play'])
        fo.fielding_assign_stats(r'E|\D', play_in_question, lineup, this_line, ['A'], ['E'])

    return this_line


# baserunner movements
def base_running2(this_line, run_play, lineup, pid, pitcher_id):

    curr_bases = gv.bases_after

    # if there is running plays, then process
    if run_play is not None:
        runners = run_play.split(';')

        for r in runners:
            this_line = runner_processor(r, this_line, lineup, pitcher_id)

        curr_bases = bases_occupied(this_line)

    # fix bases_after to correct length
    # replace runs-scored with -
    gv.bases_after = gv.bases_after.replace('R', '-')

    if len(gv.bases_after) > 3:
        # only replace first occurrence
        gv.bases_after = gv.bases_after.replace('-', '', 1)

    # replace processed outs (FO/DP) with -
    gv.bases_after = gv.bases_after.replace('X', '-')

    # replace the empty bases - 0 with '-'
    gv.bases_after = gv.bases_after.replace('0', '-')
    gv.bases_after = gv.bases_after[:3]

    # now check for stand-still runners
    # first base
    if re.search(r'^1', gv.bases_after):
        this_line['after_1B'] = this_line['before_1B']

    # second base
    if re.search(r'^.2', gv.bases_after):
        this_line['after_2B'] = this_line['before_2B']

    if re.search(r'3$', gv.bases_after):
        # stay put
        this_line['after_3B'] = this_line['before_3B']

    # if DP advanced runners with NO run play (and not SB/CS)
    if bool(re.search(r'DP', this_line['play'])) and bool(run_play is None) and \
            not(bool(re.search('(SB|CS)', this_line['play']))):
        if gv.bases_after[0] == 'B':
            this_line['after_1B'] = pid
        elif gv.bases_after[0] == '1':
            this_line['after_1B'] = this_line['before_1B']  # R1 did not run
        elif gv.bases_after[1] == '1':
            this_line['after_2B'] = this_line['before_1B']
        elif gv.bases_after[1] == '2':
            this_line['after_2B'] = this_line['before_2B']  # R2 did not run
        elif gv.bases_after[2] == '2':
            this_line['after_3B'] = this_line['before_2B']
        elif gv.bases_after[2] == '3':
            this_line['after_3B'] = this_line['before_3B']  # R3 did not run
        elif gv.bases_after == '---':
            pass  # do nothing
        else:
            print('AWKWARD DOUBLE PLAY?', curr_bases, this_line['play'], gv.bases_after)

    # turner check: SB with runner that did not move
    # if bool(re.search('(SB|CS)', this_line['play'])) and pid == 'goodb001':
    #     print(this_line['play'], '\n', curr_bases, gv.bases_after)

    # if gv.bases_after != curr_bases:
        # print(this_line['play'], gv.bases_after, '=>', curr_bases)

    return this_line


# one-by-one base runner movements
def runner_processor(runner, this_line, lineup, pitcher_id):

    # assign pitcher_id to short form to match conversion from outside functions
    hid = pitcher_id  # hurler_id

    # scored
    if re.search(r'-H', runner):
        this_line['runs_scored'] += 1

        # stat add: R
        st = ['R']
        # pitch add: R
        pt = ['R']

        if re.search(r'3-', runner):
            gv.bases_after = gv.bases_after.replace('3', 'R')
            sc.stat_collector(this_line['before_3B'], lineup, this_line, st)
        elif re.search(r'2-', runner):
            gv.bases_after = gv.bases_after.replace('2', 'R')
            sc.stat_collector(this_line['before_2B'], lineup, this_line, st)
        elif re.search(r'1-', runner):
            gv.bases_after = gv.bases_after.replace('1', 'R')
            sc.stat_collector(this_line['before_1B'], lineup, this_line, st)
        elif bool(re.search(r'B-', runner)) and \
                (not(re.search(r'^(H/|HR|([0-9]+)?E)', this_line['play']))):
            sc.stat_collector(this_line['playerID'], lineup, this_line, st)

        # check rbi awarded or not
        if bool(re.search(r'[B123]-H([(UR)/THE0-9]+)?(\((NR|NORBI)\))', runner)) | \
                bool(re.search(r'^FC.*X', this_line['play'])) | \
                bool(re.search(r'E.*[B123]-H(?!\(RBI\))', this_line['play'])) | \
                bool(re.search(r'DP|WP', this_line['play'])):
            # no RBI recorded
            pass
        else:
            # if not BALK, then record RBI
            if not(bool(re.search(r'^BK', this_line['play']))):
                # stat add: RBI
                st = ['RBI']
                sc.stat_collector(this_line['playerID'], lineup, this_line, st)

        # check earned run counted or not
        if not (re.search(r'[B123]-H([/THE0-9NOBI]+)?\(UR\)', runner)):
            pt.append('ER')

        po.pitch_collector(hid, lineup, this_line, pt)

    # stay put
    elif bool(re.search(r'3-3', runner)) | bool(re.search(r'3X3\(([0-9]+)?E', runner)):
        this_line['after_3B'] = this_line['before_3B']
    elif bool(re.search(r'2-2', runner)) | bool(re.search(r'2X2\(([0-9]+)?E', runner)):
        this_line['after_2B'] = this_line['before_2B']
    elif bool(re.search(r'1-1', runner)) | bool(re.search(r'1X1\(([0-9]+)?E', runner)):
        this_line['after_1B'] = this_line['before_1B']

    # advanced
    elif bool(re.search(r'2-3', runner)) | bool(re.search(r'2X3\(([0-9]+)?E', runner)):

        # keep everything before last two characters, then tack on the second last character
        gv.bases_after = gv.bases_after[:len(gv.bases_after)-2] + '-' + \
                         gv.bases_after[len(gv.bases_after)-2:len(gv.bases_after)-1]
        this_line['after_3B'] = this_line['before_2B']

    elif bool(re.search(r'1-2', runner)) | bool(re.search(r'1X2\(([0-9]+)?E', runner)):

        # remove the 2B runner (either - or 2, this should have moved first based on running event order
        # e.g. .2-H;1-2
        # curr_bases = gv.bases_after
        gv.bases_after = gv.bases_after[:len(gv.bases_after)-3] + \
                         gv.bases_after[len(gv.bases_after)-3:len(gv.bases_after)-2] + \
                         gv.bases_after[len(gv.bases_after)-1:]
        # if this made it too short, tack on '-' behind it. e.g. 13 is actually -13
        if len(gv.bases_after) < 3:
            # print(curr_bases, gv.bases_after, this_line['play'])
            gv.bases_after = gv.bases_after.replace('1', '-1')
        this_line['after_2B'] = this_line['before_1B']

    elif bool(re.search(r'1-3', runner)) | bool(re.search(r'1X3\(([0-9]+)?E', runner)):

        # remove the 2B and 3B runners; this should have moved already
        gv.bases_after = gv.bases_after[:len(gv.bases_after)-2]
        # tack on bases if missing; could be SF, SH, or a single, etc.
        if len(gv.bases_after) < 2:
            gv.bases_after = gv.bases_after.replace('1', '-1')
        if len(gv.bases_after) < 3:
            gv.bases_after = gv.bases_after.replace('1', '-1')
        this_line['after_3B'] = this_line['before_1B']

    # Errors from play that should have been made; batter on base to error handled further below
    if bool(re.search(r'[123]X[123H]\([1-9]?E[1-9/TH]+\)', runner)):
        error_play = re.sub(r'[123]X[123H]\(([E1-9/TH]+)\)', '\\1', runner)
        fo.fielding_assign_stats(r'E|\D', error_play, lineup, this_line, ['A'], ['E'])

    # Errors leading to advanced
    if bool(re.search(r'[B123]-[123H]\([1-9]?E[1-9/TH]+\)', runner)):
        error_throw = re.sub(r'[B123]-[123H]\(([E1-9/TH]+)\)', '\\1', runner)
        fo.fielding_assign_stats(r'E|\D', error_throw, lineup, this_line, ['A'], ['E'])

    # remove runners that are explicitly out
    if re.search(r'[123]X[123H]', runner):

        # but not FC nor the error above or DP / TP
        if not(bool(re.search(r'^FC', this_line['play']))) and not(bool(re.search(r'E', runner))) and \
                not(bool(re.search(r'(DP|TP)', this_line['play']))):
            this_line['outs'] += 1

            # process fielding
            fo.fielding_assign_stats(r'.*\(|\D', runner, lineup, this_line, ['A'], ['PO'])

        # record fielding for DP -- OR -- is FC but NO ERROR
        if bool(re.search(r'(DP|TP)', this_line['play'])) or \
                (bool(re.search(r'^FC', this_line['play'])) and not(bool(re.search(r'E', runner)))):
            fo.fielding_assign_stats(r'.*\(|\D', runner, lineup, this_line, ['A'], ['PO'])

        # first character is runner
        the_runner = runner[0]
        gv.bases_after = gv.bases_after.replace(the_runner, '-')

    # handle weird outs for the batter previously marked on base and NOT Error, e.g. not BX1(6E1)
    if bool(re.search(r'BX[123H]', runner)) and not(bool(re.search(r'E', runner))) and \
            not(bool(re.search(r'^([0-9]+)?E', this_line['play']))):
        this_line['outs'] += 1

        # stat add: AB, PA -- if NOT already added on a hit or DP (incl. FC.*DP)
        if not(bool(re.search(r'^((S|D|T)([1-9]+)?/|H/|HR|DGR)', this_line['play']))) and \
                not(bool(re.search(r'DP', this_line['play']))):
            st = ['AB', 'PA']
            sc.stat_collector(this_line['playerID'], lineup, this_line, st)

            # pitch add: IP, BF, H
            # pt = ['IP', 'BF', 'H']
            print('WEIRD OUTS: ', this_line['play'])

        # handle the now existing runner
        if this_line['after_1B'] == this_line['playerID']:
            this_line['after_1B'] = 'X'
        if this_line['after_2B'] == this_line['playerID']:
            this_line['after_2B'] = 'X'
        if this_line['after_3B'] == this_line['playerID']:
            this_line['after_3B'] = 'X'
        if re.search(r'(H[1-9]|HR).*\..*BXH', this_line['play']):
            this_line['runs_scored'] -= 1

        # process fielding
        # pujols check:
        if bool(re.search(r'DP\.1X1\([12456789]+3\)', this_line['play'])):
            print("BATTER", this_line['play'])
        fo.fielding_assign_stats(r'.*\(|\D', runner, lineup, this_line, ['A'], ['PO'])

    # batter on base due to error
    if bool(re.search(r'BX[123H]\(([0-9]+)?E', runner)) | \
            bool(re.search(r'^([0-9]+)?E.*BX[123H]', this_line['play'])):

        # move batter
        if re.search(r'BX1', runner):
            gv.bases_after = 'B' + gv.bases_after
            this_line['after_1B'] = this_line['playerID']
        elif re.search(r'BX2', runner):
            gv.bases_after = '-B' + gv.bases_after
            this_line['after_2B'] = this_line['playerID']
        elif re.search(r'BX3', runner):
            gv.bases_after = '--B' + gv.bases_after
            this_line['after_3B'] = this_line['playerID']
        elif re.search(r'BXH', runner):
            gv.bases_after = '---'
            this_line['runs_scored'] += 1

            # no rbi for this one.
            st = ['R']
            sc.stat_collector(this_line['playerID'], lineup, this_line, st)
            # definitely an unearned run too
            pt = ['R']
            po.pitch_collector(hid, lineup, this_line, pt)

        # process fielding - only for errors generated from the running plays
        # the errors from actual plays already processed in play_processor
        if bool(re.search(r'E', runner)):
            fo.fielding_assign_stats(r'.*\(|\D', runner, lineup, this_line, ['A'], ['E'])

        # otherwise, nothing happens, as the E is recorded -- most likely for the throw; no assist, no put out

    # batter on base due to PB or WP or E
    if bool(re.search(r'B-1', runner)) and bool(re.search(r'^K\+(WP|PB|E).*B-1', this_line['play'])):
        this_line['outs'] -= 1
        this_line['after_1B'] = this_line['playerID']
        gv.bases_after = 'B' + gv.bases_after[1:]  # to replace the initial - placed by the K

    # if batter on base explicitly - probably advance on throw or just defense fell asleep
    if bool(re.search(r'B-[123]', runner)):
        bases_before = gv.bases_after
        batter_move = re.sub(r'.*(B-[123]).*', '\\1', runner)
        if bool(re.search(r'-1', batter_move)):
            this_line['after_1B'] = this_line['playerID']
            if len(gv.bases_after) == 4 and not(bool(re.search(r'^B', gv.bases_after))):
                gv.bases_after = 'B' + gv.bases_after[1:]
        elif bool(re.search(r'-2', batter_move)):
            this_line['after_2B'] = this_line['playerID']
            gv.bases_after = '0B' + gv.bases_after[2:]  # if Error on play, this should overwrite B-- to 0B--
        else:
            this_line['after_3B'] = this_line['playerID']
            gv.bases_after = '00B' + gv.bases_after[3:]
        # print("Batter advanced:", this_line['play'], bases_before, gv.bases_after)
        '''
        #  NOTE: This will OVERWRITE 'R', runs scored, however, the 'R' gets replaced in base_running2
        #  This is not an issue as the 'runs_scored' are recorded in 'this_line' separately
        #  Runner movement for the bases is still correct, so there is no stat issue overwriting the error plays.
        '''

    return this_line


# track any runner movement for event
def check_runner_movement(this_line):
    # this will ignore SOLO HOME RUNS!
    if this_line['before_1B'] != this_line['after_1B']:
        return False
    if this_line['before_2B'] != this_line['after_2B']:
        return False
    if this_line['before_3B'] != this_line['after_3B']:
        return False
    return True


# bases occupied
def bases_occupied(this_line):

    # before
    bases_taken = []
    if this_line['before_1B']:
        bases_taken.append('1')
    else:
        bases_taken.append('-')
    if this_line['before_2B']:
        bases_taken.append('2')
    else:
        bases_taken.append('-')
    if this_line['before_3B']:
        bases_taken.append('3')
    else:
        bases_taken.append('-')
    bases_taken = ''.join(map(str, bases_taken))

    return bases_taken
