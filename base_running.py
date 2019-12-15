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

    # new_line = [this_line['1B_after'], this_line['2B_after'], this_line['3B_after'], this_line['runs_scored']]

    # return new_line
    return this_line
