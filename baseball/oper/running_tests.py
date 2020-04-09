# this file is to run tests of the oper files ONLY
from . import import_retrosheet as ir
from . import process_imports as pi
from . import generate_statistics as gs


# import Year; print True if completed
print("Import Completed: ", ir.import_data(2018))

# print True if this succeeds
print("Processing Completed: ", pi.process_data_single_team(2018, 'TOR'))

# print True if generating stats succeeds
print("Stats Generated: ", gs.generate_stats(2018, 'TOR'))
