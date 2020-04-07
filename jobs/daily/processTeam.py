from django_extensions.management.jobs import DailyJob
from ...oper import process_imports as pi
from ...oper import error_logger as el
from ...oper import check_latest_imports as chk


# this job processes a team for specific YEAR
# Once tested, this should run DAILY
class Job(DailyJob):
    help = "Processes event file for a team in X year"

    def execute(self):

        # get a list of the years that HAVE been imported
        year_choices = chk.get_years()
        print(year_choices)

        # loop through years for FIRST instance of a team choice option
        # year_choices.reverse()  # don't need to reverse order in prod, should be smallest year

        team = ''
        year = 0
        for y in year_choices:
            # get list of teams not processed
            team_choices = chk.check_teams(y, 'process_team')

            if len(team_choices) > 0:
                print(y, team_choices)
                team = team_choices[0]  # just take the first one
                year = y
                break

        # check if year is 0 still
        if int(year) > 0:
            status = pi.process_data_single_team(year, team)

            # these messages should be stored in /var/log/syslog
            # use cat syslog | grep CRON to view
            if status:
                print("Process Team... Success")
                return True
            else:
                print("Process Team... Failed")
                return False
        else:
            print("No teams to process... Wait for next Year import.")
            return False
