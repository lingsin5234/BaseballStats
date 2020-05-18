from django_extensions.management.jobs import WeeklyJob
from ...oper import import_retrosheet as ir
from ...oper import error_logger as el
from ...oper import check_latest_imports as chk


# this job imports a certain Year from the retrosheet.org
# Once tested, this should run WEEKLY
class Job(WeeklyJob):
    help = "Imports a year of files from Retrosheet.org"

    def execute(self):

        # get a list of the years not imported yet
        year_choices = chk.check_years()
        print(year_choices)
        year = max(year_choices)
        print(year)
        status = ir.import_data(str(year))

        # these messages should be stored in /var/log/syslog
        # use cat syslog | grep CRON to view
        if status:
            print("Import Year... Success")
            return True
        else:
            print("Import Year... Failed")
            return False
