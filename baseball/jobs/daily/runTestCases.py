from django_extensions.management.jobs import DailyJob
from baseball.oper import generate_statistics as gs
from baseball.oper import check_latest_imports as chk
from baseball.oper import automated_tests as aut
import sys


# this job can be run AD_HOC; and will not be added to crontab
class Job(DailyJob):
    help = "Run Ad-Hoc Test Case given YEAR argument"

    def execute(self):

        stat_cats = ['batting', 'pitching', 'fielding']  # or split into 3 separate jobs?
        years = chk.get_stats_gen_complete_years()
        for yr in years:
            # run some tests
            aut.import_test_cases(yr)
            aut.run_test_cases('batting', yr)
            # aut.run_test_cases('pitching', year[0])
            aut.run_test_cases('fielding', yr)

        return True
