# tracking base running movement
# libraries
import re
import stat_collector as sc
import global_variables as gv
import pitcher_oper as po


# stolen base tracking
def steal_processor(this_line, lineup):

    # check if steal, then which base(s)
    if re.search(r'SB', this_line['play']):
        if re.search(r'SB2', this_line['play']):
            # if NOT an error on throwing
            if not(re.search(r'SB2.1-[23H]\(([0-9]+)?E([0-9]+)?', this_line['play'])):
                this_line['2B_after'] = this_line['1B_before']

            # stat add: SB
            st = ['SB']
            sc.stat_collector(this_line['1B_before'], lineup, this_line, st)

        if re.search(r'SB3', this_line['play']):
            # if NOT an error on throwing
            if not (re.search(r'SB3.2-[3H]\(([0-9]+)?E([0-9]+)?', this_line['play'])):
                this_line['3B_after'] = this_line['2B_before']

            # stat add: SB
            st = ['SB']
            sc.stat_collector(this_line['2B_before'], lineup, this_line, st)

        if re.search(r'SBH', this_line['play']):
            # if NOT an error on throwing
            if not (re.search(r'SBH.3-[H]\(([0-9]+)?E([0-9]+)?', this_line['play'])):
                this_line['runs_scored'] += 1

            # stat add: SB, R
            st = ['SB', 'R']
            sc.stat_collector(this_line['3B_before'], lineup, this_line, st)

    # check if caught stealing, then which base(s)
    if re.search(r'CS', this_line['play']):
        if re.search(r'CS2', this_line['play']):
            # stat add: CS
            st = ['CS']
            sc.stat_collector(this_line['1B_before'], lineup, this_line, st)

        if re.search(r'CS3', this_line['play']):
            # stat add: CS
            st = ['CS']
            sc.stat_collector(this_line['2B_before'], lineup, this_line, st)

        if re.search(r'CSH', this_line['play']):
            # stat add: CS
            st = ['CS']
            sc.stat_collector(this_line['3B_before'], lineup, this_line, st)

    return this_line


# baserunner movements
def base_running2(this_line, run_play, lineup, pitcher_id):

    # if there is running plays, then process
    if run_play is not None:
        runners = run_play.split(';')

        for r in runners:
            this_line = runner_processor(r, this_line, lineup, pitcher_id)

    return this_line


# baserunner movements
def base_running(this_line, lineup, pitcher_id):
    
    # case: FO|FC|DP
    if re.search(r'(FC|FO|DP)', this_line['play']):
        # find the out, move appropriate
        # R1 is out
        if re.search(r'\(1\)', this_line['play']):
            # batter on first unless DP
            if this_line['1B_after'] != 'X':
                this_line['1B_after'] = this_line['playerID']
        # R2 is out
        if re.search(r'\(2\)', this_line['play']):
            # batter on first unless DP
            if this_line['1B_after'] != 'X':
                this_line['1B_after'] = this_line['playerID']
            # R1 on 2nd unless DP
            if (this_line['2B_after'] != 'X') & \
                    (this_line['2B_after'] is not None):
                this_line['2B_after'] = this_line['1B_before']
            # R3 stays on base
            if (this_line['3B_after'] != 'X') & \
                    (this_line['3B_before'] is not None) & \
                    bool(re.search(r'\..*3(-|X)H', this_line['play'])):
                this_line['3B_after'] = this_line['3B_before']

        # R3 is out
        if re.search(r'\(3\)', this_line['play']):
            # batter on first unless DP
            if this_line['1B_after'] != 'X':
                this_line['1B_after'] = this_line['playerID']
            # R1 on 2nd unless DP
            if (this_line['2B_after'] != 'X') & \
                    (this_line['2B_after'] is not None):
                this_line['2B_after'] = this_line['1B_before']
            # R2 on 3rd unless DP
            if (this_line['3B_after'] != 'X') & \
                    (this_line['3B_after'] is not None):
                this_line['3B_after'] = this_line['2B_before']

    # case: base movement(s)
    if re.search(r'\.[B123](-|X)[123H]', this_line['play']):
        # separate for multiple runners
        if re.search(r';', this_line['play']):
            runners = this_line['play'].split('.')[1].split(';')

            for r in runners:
                this_line = runner_processor(r, this_line, lineup, pitcher_id)

        # single baserunner
        else:
            runners = this_line['play'].split('.')[1].split(';')[0]
            this_line = runner_processor(runners, this_line, lineup, pitcher_id)

    # case: steal or CS
    # not a double/triple steal then process stand-still runners
    if not (re.search(r'SB.*SB', this_line['play'])):
        if re.search(r'SB2(?!\.)', this_line['play']):
            if (this_line['3B_before'] is not None) & (this_line['3B_after'] is None):
                this_line['3B_after'] = this_line['3B_before']
        if re.search(r'SB3(?!\.)', this_line['play']):
            if (this_line['1B_before'] is not None) & (this_line['1B_after'] is None):
                this_line['1B_after'] = this_line['1B_before']
        if re.search(r'SBH(?!\.)', this_line['play']):
            if (this_line['1B_before'] is not None) & (this_line['1B_after'] is None):
                this_line['1B_after'] = this_line['1B_before']
            if (this_line['2B_before'] is not None) & (this_line['2B_after'] is None):
                this_line['2B_after'] = this_line['2B_before']

    # case: retain the runners that did not move
    # R3 did not move and was not out
    if bool(not (re.search(r'\..*3(-|X)[3H]', this_line['play']))) & \
            (this_line['3B_after'] != 'X') & \
            (this_line['3B_before'] is not None) & \
            (this_line['3B_after'] != this_line['playerID']):
        this_line['3B_after'] = this_line['3B_before']

    # R2 did not move and was not out
    if bool(not (re.search(r'\..*2(-|X)[23H]', this_line['play']))) & \
            (this_line['2B_after'] != 'X') & \
            (this_line['2B_before'] is not None) & \
            (this_line['2B_after'] != this_line['playerID']):
        this_line['2B_after'] = this_line['2B_before']

    # R1 did not move and was not out
    if bool(not (re.search(r'\..*1(-|X)[123H]', this_line['play']))) & \
            (this_line['1B_after'] != 'X') & \
            (this_line['1B_before'] is not None) & \
            (this_line['1B_after'] != this_line['playerID']):
        this_line['1B_after'] = this_line['1B_before']

    # remove the X's
    if this_line['1B_after'] == 'X':
        this_line['1B_after'] = None
    if this_line['2B_after'] == 'X':
        this_line['2B_after'] = None
    if this_line['3B_after'] == 'X':
        this_line['3B_after'] = None

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
            sc.stat_collector(this_line['3B_before'], lineup, this_line, st)
        elif re.search(r'2-', runner):
            sc.stat_collector(this_line['2B_before'], lineup, this_line, st)
        elif re.search(r'1-', runner):
            sc.stat_collector(this_line['1B_before'], lineup, this_line, st)
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
        this_line['3B_after'] = this_line['3B_before']
    elif bool(re.search(r'2-2', runner)) | bool(re.search(r'2X2\(([0-9]+)?E', runner)):
        this_line['2B_after'] = this_line['2B_before']
    elif bool(re.search(r'1-1', runner)) | bool(re.search(r'1X1\(([0-9]+)?E', runner)):
        this_line['1B_after'] = this_line['1B_before']

    # advanced
    elif bool(re.search(r'2-3', runner)) | bool(re.search(r'2X3\(([0-9]+)?E', runner)):
        this_line['3B_after'] = this_line['2B_before']
    elif bool(re.search(r'1-2', runner)) | bool(re.search(r'1X2\(([0-9]+)?E', runner)):
        this_line['2B_after'] = this_line['1B_before']
    elif bool(re.search(r'1-3', runner)) | bool(re.search(r'1X3\(([0-9]+)?E', runner)):
        this_line['3B_after'] = this_line['1B_before']

    # remove runners that are explicitly out but not FC nor the error above
    if re.search(r'[123]X[123H]', runner):
        if bool(not(re.search(r'^FC', this_line['play']))) & bool(not(re.search(r'E', runner))):
            this_line['outs'] += 1

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
        if this_line['1B_after'] == this_line['playerID']:
            this_line['1B_after'] = 'X'
        if this_line['2B_after'] == this_line['playerID']:
            this_line['2B_after'] = 'X'
        if this_line['3B_after'] == this_line['playerID']:
            this_line['3B_after'] = 'X'
        if re.search(r'(H[1-9]|HR).*\..*BXH', this_line['play']):
            this_line['runs_scored'] -= 1

    # batter on base due to error
    if bool(re.search(r'BX[123H]\(([0-9]+)?E', runner)) | \
            bool(re.search(r'^([0-9]+)?E.*BX[123H]', this_line['play'])):

        # move batter
        if re.search(r'BX1', runner):
            this_line['1B_after'] = this_line['playerID']
        elif re.search(r'BX2', runner):
            this_line['2B_after'] = this_line['playerID']
        elif re.search(r'BX3', runner):
            this_line['3B_after'] = this_line['playerID']
        elif re.search(r'BXH', runner):
            this_line['runs_scored'] += 1

            # no rbi for this one.
            st = ['R']
            sc.stat_collector(this_line['playerID'], lineup, this_line, st)
            # definitely an unearned run too
            pt = ['R']
            po.pitch_collector(hid, lineup, this_line, pt)

    return this_line


# track any runner movement for event
def check_runner_movement(this_line):
    # this will ignore SOLO HOME RUNS!
    if this_line['1B_before'] != this_line['1B_after']:
        return False
    if this_line['2B_before'] != this_line['2B_after']:
        return False
    if this_line['3B_before'] != this_line['3B_after']:
        return False
    return True
