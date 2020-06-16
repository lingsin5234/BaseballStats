# libraries
import re
from . import pitcher_oper as po
from . import base_running as br
from . import global_variables as gv
from . import fielding_oper as fo


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
        this_line = br.steal_processor(this_line, lineup)

    if bool(re.search(r'CS', begin_play)) and not(bool(re.search(r'POCS', begin_play))):
        # run steal_processor
        this_line = br.steal_processor(this_line, lineup)

    if bool(re.search(r'PO', begin_play)) and not(bool(re.search(r'POCS', begin_play))):
        pt = ['POA']
        # if not an error then PO successful
        if not(bool(re.search(r'E', begin_play))):
            this_line['outs'] += 1
            pt.append('PO')

            # figure out which base is out
            if re.search(r'PO1', begin_play):
                gv.bases_after = gv.bases_after.replace('1', 'X')
            elif re.search(r'PO2', begin_play):
                gv.bases_after = gv.bases_after.replace('2', 'X')
            elif re.search(r'PO3', begin_play):
                gv.bases_after = gv.bases_after.replace('3', 'X')

            # fielding for Pick-Offs (PO)
            if re.search(r'PO[123]\([1-9E/TH]+\)', begin_play):

                # runner movement handled in the base_running
                po_play = re.sub(r'.*PO[123]\(([1-9E/TH]+)\).*', '\\1', begin_play)
                if bool(re.search('E', po_play)):
                    fo.fielding_assign_stats(r'E|\D', po_play, lineup, this_line, ['A'], ['E'])
                else:
                    fo.fielding_assign_stats(r'\D', po_play, lineup, this_line, ['A'], ['PO'])

    if re.search(r'POCS', begin_play):
        pt = ['POA']
        # if not an error then PO successful
        if not(bool(re.search(r'E', begin_play))):
            this_line['outs'] += 1
            pt.append('PO')

            # figure out which base is out
            if re.search(r'PO1', begin_play):
                gv.bases_after = gv.bases_after.replace('1', 'X')
            elif re.search(r'PO2', begin_play):
                gv.bases_after = gv.bases_after.replace('2', 'X')
            elif re.search(r'PO3', begin_play):
                gv.bases_after = gv.bases_after.replace('3', 'X')

            # run steal_processor - fielding taken care of here as well
            this_line = br.steal_processor(this_line, lineup)

        # else error
        else:
            pocs_play = re.sub(r'.*POCS[123H]\(([E1-9/TH]+)\).*', '\\1', begin_play)
            fo.fielding_assign_stats(r'E|\D', pocs_play, lineup, this_line, ['A'], ['E'])

    if re.search(r'DI', begin_play):
        pt = ['DI']

    if pt is not None:
        po.pitch_collector(hid, lineup, this_line, pt)

    return this_line
