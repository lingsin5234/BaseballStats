from django_extensions.management.jobs import WeeklyJob
from ...oper import extract_teams_players as etp
from ...oper import check_latest_imports as chk


# this job extracts Team and Player names from TEAM and .ROS files
class Job(WeeklyJob):
    help = "Extracts Team and Player names from TEAM and .ROS files"

    def execute(self):

        # run the extract_player/teams
        year_choices = chk.get_years()
        print(year_choices)
        year = min(year_choices)
        print(year)
        status1 = etp.extract_teams(year)
        status2 = etp.extract_players(year)

        # these messages should be stored in /var/log/syslog
        # use cat syslog | grep CRON to view
        if status1 and status2:
            print("Extract Names... Success")
            return True
        else:
            print("Extract Names... Failed")
            return False
