# tracking base running movement
# libraries
import re
import stat_collector as sc


# stolen base tracking
def steal_processor(this_line):

    # check if steal, then which base(s)
    if re.search(r'SB', str(this_line['play'])):
        if re.search(r'SB2', str(this_line['play'])):
            # if NOT an error on throwing
            if not(re.search(r'SB2.1-[23H]\(([0-9]+)?E([0-9]+)?', str(this_line['play']))):
                this_line['2B_after'] = this_line['1B_before']

            # stat add: SB
            st = ['SB']
            sc.stat_collector(this_line['1B_before'], this_line, st)

        if re.search(r'SB3', str(this_line['play'])):
            # if NOT an error on throwing
            if not (re.search(r'SB3.2-[3H]\(([0-9]+)?E([0-9]+)?', str(this_line['play']))):
                this_line['3B_after'] = this_line['2B_before']

            # stat add: SB
            st = ['SB']
            sc.stat_collector(this_line['2B_before'], this_line, st)

        if re.search(r'SBH', str(this_line['play'])):
            # if NOT an error on throwing
            if not (re.search(r'SBH.3-[H]\(([0-9]+)?E([0-9]+)?', str(this_line['play']))):
                this_line['runs_scored'] += 1

            # stat add: SB, R
            st = ['SB', 'R']
            sc.stat_collector(this_line['3B_before'], this_line, st)

    # new_line = [this_line['1B_after'], this_line['2B_after'], this_line['3B_after'], this_line['runs_scored']]

    # return new_line
    return this_line
