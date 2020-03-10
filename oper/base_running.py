# tracking base running movement
# libraries
import re
from . import stat_collector as sc
from . import global_variables as gv
from . import pitcher_oper as po


# stolen base tracking
def steal_processor(this_line, lineup):

    # check if steal, then which base(s)
    if re.search(r'SB', this_line['play']):
        if re.search(r'SB2', this_line['play']):
            # if NOT an error on throwing
            if not(re.search(r'SB2.1-[23H]\(([0-9]+)?E([0-9]+)?', this_line['play'])):
                this_line['after_2B'] = this_line['before_1B']
                gv.bases_after = '-1' + gv.bases_after[len(gv.bases_after)-2:]

            # stat add: SB
            st = ['SB']
            sc.stat_collector(this_line['before_1B'], lineup, this_line, st)

        if re.search(r'SB3', this_line['play']):
            # if NOT an error on throwing
            if not (re.search(r'SB3.2-[3H]\(([0-9]+)?E([0-9]+)?', this_line['play'])):
                this_line['after_3B'] = this_line['before_2B']
                gv.bases_after = gv.bases_after[:len(gv.bases_after)-2] + '-2' + \
                                 gv.bases_after[len(gv.bases_after)-1:]

            # stat add: SB
            st = ['SB']
            sc.stat_collector(this_line['before_2B'], lineup, this_line, st)

        if re.search(r'SBH', this_line['play']):
            # if NOT an error on throwing
            if not (re.search(r'SBH.3-[H]\(([0-9]+)?E([0-9]+)?', this_line['play'])):
                this_line['runs_scored'] += 1
                gv.bases_after = gv.bases_after.replace('3', 'R')

            # stat add: SB, R
            st = ['SB', 'R']
            sc.stat_collector(this_line['before_3B'], lineup, this_line, st)

    # check if caught stealing, then which base(s)
    if re.search(r'CS', this_line['play']):
        if re.search(r'CS2', this_line['play']):
            gv.bases_after = gv.bases_after.replace('1', 'X')
            # stat add: CS
            st = ['CS']
            sc.stat_collector(this_line['before_1B'], lineup, this_line, st)

        if re.search(r'CS3', this_line['play']):
            gv.bases_after = gv.bases_after.replace('2', 'X')
            # stat add: CS
            st = ['CS']
            sc.stat_collector(this_line['before_2B'], lineup, this_line, st)

        if re.search(r'CSH', this_line['play']):
            gv.bases_after = gv.bases_after.replace('3', 'X')
            # stat add: CS
            st = ['CS']
            sc.stat_collector(this_line['before_3B'], lineup, this_line, st)

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
    if bool(re.search(r'DP', this_line['play'])) & bool(run_play is None) & \
            bool(not(re.search('(SB|CS)', this_line['play']))):
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
        elif bool(re.search(r'B-', runner)) & \
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
        gv.bases_after = gv.bases_after[:len(gv.bases_after)-3] + \
                         gv.bases_after[len(gv.bases_after)-3:len(gv.bases_after)-2] + \
                         gv.bases_after[len(gv.bases_after)-1:]
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

    # remove runners that are explicitly out but not FC nor the error above or DP/TP
    if re.search(r'[123]X[123H]', runner):
        if bool(not(re.search(r'^FC', this_line['play']))) & bool(not(re.search(r'E', runner))) & \
                bool(not(re.search(r'(DP|TP)', this_line['play']))):
            this_line['outs'] += 1

        # first character is runner
        the_runner = runner[0]
        gv.bases_after = gv.bases_after.replace(the_runner, '-')

    # handle weird outs for the batter previously marked on base and NOT Error, e.g. BX1(6E1)
    if bool(re.search(r'BX[123H]', runner)) & bool(not(re.search(r'E', runner))) & \
            bool(not(re.search(r'^([0-9]+)?E', this_line['play']))):
        this_line['outs'] += 1

        # stat add: AB, PA -- if NOT already added on a hit or DP (incl. FC.*DP)
        if bool(not(re.search(r'^((S|D|T)([1-9]+)?/|H/|HR|DGR)', this_line['play']))) & \
                bool(not(re.search(r'DP', this_line['play']))):
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

    # batter on base due to PB or WP
    if bool(re.search(r'^K\+(WP|PB).*B-1', this_line['play'])):
        this_line['outs'] -= 1
        this_line['after_1B'] = this_line['playerID']
        gv.bases_after = 'B' + gv.bases_after[1:]  # to replace the initial - placed by the K

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