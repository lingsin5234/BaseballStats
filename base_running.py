# tracking base running movement
# libraries
import re
import stat_collector as sc
import global_variables as gv


# stolen base tracking
def steal_processor(this_line):

    # check if steal, then which base(s)
    if re.search(r'SB', this_line['play'].values[0]):
        if re.search(r'SB2', this_line['play'].values[0]):
            # if NOT an error on throwing
            if not(re.search(r'SB2.1-[23H]\(([0-9]+)?E([0-9]+)?', this_line['play'].values[0])):
                this_line['2B_after'].values[0] = this_line['1B_before'].values[0]

            # stat add: SB
            st = ['SB']
            sc.stat_collector(this_line['1B_before'].values[0], this_line, st)

        if re.search(r'SB3', this_line['play'].values[0]):
            # if NOT an error on throwing
            if not (re.search(r'SB3.2-[3H]\(([0-9]+)?E([0-9]+)?', this_line['play'].values[0])):
                this_line['3B_after'].values[0] = this_line['2B_before'].values[0]

            # stat add: SB
            st = ['SB']
            sc.stat_collector(this_line['2B_before'].values[0], this_line, st)

        if re.search(r'SBH', this_line['play'].values[0]):
            # if NOT an error on throwing
            if not (re.search(r'SBH.3-[H]\(([0-9]+)?E([0-9]+)?', this_line['play'].values[0])):
                this_line['runs_scored'].values[0] += 1

            # stat add: SB, R
            st = ['SB', 'R']
            sc.stat_collector(this_line['3B_before'].values[0], this_line, st)

    # check if caught stealing, then which base(s)
    if re.search(r'CS', this_line['play'].values[0]):
        if re.search(r'CS2', this_line['play'].values[0]):
            # stat add: CS
            st = ['CS']
            sc.stat_collector(this_line['1B_before'].values[0], this_line, st)

        if re.search(r'CS3', this_line['play'].values[0]):
            # stat add: CS
            st = ['CS']
            sc.stat_collector(this_line['2B_before'].values[0], this_line, st)

        if re.search(r'CSH', this_line['play'].values[0]):
            # stat add: CS
            st = ['CS']
            sc.stat_collector(this_line['3B_before'].values[0], this_line, st)

    return this_line


# baserunner movements
def base_running(this_line):
    
    # case: FO|FC|DP
    if re.search(r'(FC|FO|DP)', this_line['play'].values[0]):
        # find the out, move appropriate
        # R1 is out
        if re.search(r'\(1\)', this_line['play'].values[0]):
            # batter on first unless DP
            if this_line['1B_after'].values[0] != 'X':
                this_line['1B_after'].values[0] = this_line['playerID'].values[0]
        # R2 is out
        if re.search(r'\(2\)', this_line['play'].values[0]):
            # batter on first unless DP
            if this_line['1B_after'].values[0] != 'X':
                this_line['1B_after'].values[0] = this_line['playerID'].values[0]
            # R1 on 2nd unless DP
            if (this_line['2B_after'].values[0] != 'X') & \
                    (this_line['2B_after'].values[0] is not None):
                this_line['2B_after'].values[0] = this_line['1B_before'].values[0]
            # R3 stays on base
            if (this_line['3B_after'].values[0] != 'X') & \
                    (this_line['3B_before'].values[0] is not None) & \
                    bool(re.search(r'\..*3(-|X)H', this_line['play'].values[0])):
                this_line['3B_after'].values[0] = this_line['3B_before'].values[0]

        # R3 is out
        if re.search(r'\(3\)', this_line['play'].values[0]):
            # batter on first unless DP
            if this_line['1B_after'].values[0] != 'X':
                this_line['1B_after'].values[0] = this_line['playerID'].values[0]
            # R1 on 2nd unless DP
            if (this_line['2B_after'].values[0] != 'X') & \
                    (this_line['2B_after'].values[0] is not None):
                this_line['2B_after'].values[0] = this_line['1B_before'].values[0]
            # R2 on 3rd unless DP
            if (this_line['3B_after'].values[0] != 'X') & \
                    (this_line['3B_after'].values[0] is not None):
                this_line['3B_after'].values[0] = this_line['2B_before'].values[0]

    # case: base movement(s)
    if re.search(r'\.[B123](-|X)[123H]', this_line['play'].values[0]):
        # separate for multiple runners
        if re.search(r';', this_line['play'].values[0]):
            runners = this_line['play'].values[0].split('.')[1].split(';')

            for r in runners:
                this_line = runner_processor(r, this_line)

            print(runners)
            print(type(this_line))
            print(this_line)
            exit()
        # single baserunner
        else:
            runners = this_line['play'].values[0].split('.')[1].split(';')[0]
            this_line = runner_processor(runners, this_line)
            print(runners)
            print(this_line)

    # case: steal or CS
    # not a double/triple steal then process stand-still runners
    if not (re.search(r'SB.*SB', this_line['play'].values[0])):
        if re.search(r'SB2(?!\.)', this_line['play'].values[0]):
            if (this_line['3B_before'].values[0] is not None) & (this_line['3B_after'].values[0] is None):
                this_line['3B_after'].values[0] = this_line['3B_before'].values[0]
        if re.search(r'SB3(?!\.)', this_line['play'].values[0]):
            if (this_line['1B_before'].values[0] is not None) & (this_line['1B_after'].values[0] is None):
                this_line['1B_after'].values[0] = this_line['1B_before'].values[0]
        if re.search(r'SBH(?!\.)', this_line['play'].values[0]):
            if (this_line['1B_before'].values[0] is not None) & (this_line['1B_after'].values[0] is None):
                this_line['1B_after'].values[0] = this_line['1B_before'].values[0]
            if (this_line['2B_before'].values[0] is not None) & (this_line['2B_after'].values[0] is None):
                this_line['2B_after'].values[0] = this_line['2B_before'].values[0]

    # case: retain the runners that did not move
    # R3 did not move and was not out
    if bool(not (re.search(r'\..*3(-|X)[3H]', this_line['play'].values[0]))) & \
            (this_line['3B_after'].values[0] != 'X') & \
            (this_line['3B_before'].values[0] is not None) & \
            (this_line['3B_after'].values[0] != this_line['playerID'].values[0]):
        this_line['3B_after'].values[0] = this_line['3B_before'].values[0]

    # R2 did not move and was not out
    if bool(not (re.search(r'\..*2(-|X)[23H]', this_line['play'].values[0]))) & \
            (this_line['2B_after'].values[0] != 'X') & \
            (this_line['2B_before'].values[0] is not None) & \
            (this_line['2B_after'].values[0] != this_line['playerID'].values[0]):
        this_line['2B_after'].values[0] = this_line['2B_before'].values[0]

    # R1 did not move and was not out
    if bool(not (re.search(r'\..*1(-|X)[123H]', this_line['play'].values[0]))) & \
            (this_line['1B_after'].values[0] != 'X') & \
            (this_line['1B_before'].values[0] is not None) & \
            (this_line['1B_after'].values[0] != this_line['playerID'].values[0]):
        this_line['1B_after'].values[0] = this_line['1B_before'].values[0]

    # remove the X's
    if this_line['1B_after'].values[0] == 'X':
        this_line['1B_after'].values[0] = None
    if this_line['2B_after'].values[0] == 'X':
        this_line['2B_after'].values[0] = None
    if this_line['3B_after'].values[0] == 'X':
        this_line['3B_after'].values[0] = None

    return this_line


# one-by-one base runner movements
def runner_processor(runner, this_line):

    # scored
    if re.search(r'-H', runner):
        this_line['runs_scored'].values[0] += 1

        # stat add: R
        st = ['R']
        if re.search(r'3-', runner):
            sc.stat_collector(this_line['3B_before'].values[0], this_line, st)
        elif re.search(r'2-', runner):
            sc.stat_collector(this_line['2B_before'].values[0], this_line, st)
        elif re.search(r'1-', runner):
            sc.stat_collector(this_line['1B_before'].values[0], this_line, st)
        elif bool(re.search(r'B-', runner)) & \
                (not(re.search(r'^(H/|HR|([0-9]+)?E)', this_line['play'].values[0]))):
            sc.stat_collector(this_line['playerID'].values[0], this_line, st)

        # check rbi awarded or not
        if bool(re.search(r'[B123]-H([(UR)/THE0-9]+)?(\((NR|NORBI)\))', runner)) | \
                bool(re.search(r'^FC.*X', this_line['play'].values[0])) | \
                bool(re.search(r'E.*[B123]-H(?!\(RBI\))', this_line['play'].values[0])) | \
                bool(re.search(r'DP|WP', this_line['play'].values[0])):
            # no RBI recorded
            pass
        else:
            # stat add: RBI
            st = ['RBI']
            sc.stat_collector(this_line['playerID'].values[0], this_line, st)

    # stay put
    elif re.search(r'3-3', runner):
        this_line['3B_after'].values[0] = this_line['3B_before'].values[0]
    elif re.search(r'2-2', runner):
        this_line['2B_after'].values[0] = this_line['2B_before'].values[0]
    elif re.search(r'1-1', runner):
        this_line['1B_after'].values[0] = this_line['1B_before'].values[0]

    # advanced
    elif re.search(r'2-3', runner):
        this_line['3B_after'].values[0] = this_line['2B_before'].values[0]
    elif re.search(r'1-2', runner):
        this_line['2B_after'].values[0] = this_line['1B_before'].values[0]
    if re.search(r'1-3', runner):
        this_line['3B_after'].values[0] = this_line['1B_before'].values[0]

    # remove runners that are explicitly out
    if re.search(r'[123]X[123H]', runner):
        this_line['outs'].values[0] += 1

    # handle weird outs for the batter previously marked on base.
    if re.search(r'BX[123H]', runner):
        this_line['outs'].values[0] += 1

        # stat add: AB, PA -- if NOT already added on a hit
        if not(re.search(r'^((S|D|T)([1-9]+)?/|H/|HR|DGR)', this_line['play'].values[0])):
            st = ['AB', 'PA']
            sc.stat_collector(this_line['playerID'].values[0], this_line, st)

        # handle the now existing runner
        if this_line['1B_after'].values[0] == this_line['playerID'].values[0]:
            this_line['1B_after'].values[0] = 'X'
        if this_line['2B_after'].values[0] == this_line['playerID'].values[0]:
            this_line['2B_after'].values[0] = 'X'
        if this_line['3B_after'].values[0] == this_line['playerID'].values[0]:
            this_line['3B_after'].values[0] = 'X'
        if re.search(r'(H[1-9]|HR).*\..*BXH', this_line['play'].values[0]):
            this_line['runs_scored'].values[0] -= 1

    return this_line
