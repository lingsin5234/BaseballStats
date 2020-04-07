from django_extensions.management.jobs import HourlyJob
from ...oper import generate_statistics as gs
from ...oper import error_logger as el
from ...oper import check_latest_imports as chk


# this job generate stats for a specific team + year
# Once tested, this should run HOURLY
class Job(HourlyJob):
    help = "Generate Stats for given Team + Year"

    def execute(self):

        # get a list of the years that HAVE been imported
        year_choices = chk.get_years()
        print(year_choices)

        # loop through years for FIRST instance of a team choice option

        team = ''
        year = 0
        for y in year_choices:
            # get list of teams already processed
            team_choices = chk.check_teams(y, 'go_generate_stats')

            if team_choices is None:
                pass
            else:
                print(y, team_choices)
                team = team_choices[0]  # just take the first one
                year = y
                break

        # check if year is 0 still
        if int(year) > 0:
            status = gs.generate_stats(year, team)

            # these messages should be stored in /var/log/syslog
            # use cat syslog | grep CRON to view
            if status:
                print("Generate Stats... Success")
                return True
            else:
                print("Generate Stats... Failed")
                return False
        else:
            print("No teams to generate stats for... Wait for next Year import.")
            return False
