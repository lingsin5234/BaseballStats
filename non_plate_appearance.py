# libraries
import re
import pitcher_oper as po


# function for processing non-plate appearances
def non_pa(this_line, begin_play, run_play, lineup, pid, hid):

    pt = None

    # if bool(re.search(r'^(WP|NP|BK|PB|FLE|OA|SB|CS|PO|DI)', begin_play)):
    if re.search(r'WP', begin_play):
        pt = ['WP']
    if re.search(r'NP', begin_play):
        pass
    if re.search(r'BK', begin_play):
        pt = ['BK']
    if re.search(r'PB', begin_play):
        pt = ['PB']
    if re.search(r'FLE', begin_play):
        pass
    if re.search(r'OA', begin_play):
        pass
    if re.search(r'SB', begin_play):
        # run steal_processor
        pass
    if bool(re.search(r'CS', begin_play)) & bool(not(re.search(r'POCS', begin_play))):
        # run steal_processor
        pass
    if bool(re.search(r'PO', begin_play)) & bool(not (re.search(r'POCS', begin_play))):
        pt = ['PO']
    if re.search(r'POCS', begin_play):
        # run steal_processor
        pt = ['PO']
    if re.search(r'DI', begin_play):
        pass

    if pt is not None:
        po.pitch_collector(hid, lineup, this_line, pt)

    return this_line
