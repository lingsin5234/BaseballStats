from django_extensions.management.jobs import WeeklyJob
from baseball.oper import generate_statistics as gs
from baseball.oper import check_latest_imports as chk
from baseball.oper import automated_tests as aut


# this job generate stats for LATEST completed year
# also run a post-run automated testing
class Job(WeeklyJob):
    help = "Generate Stats for given Team + Year"

    def execute(self):

        stat_cats = ['batting', 'pitching', 'fielding']  # or split into 3 separate jobs?

        # get a list of the years that HAVE been imported
        # year_choices = chk.get_years()
        # print(year_choices)

        # get list of completely processed years but not done stats generation
        year = chk.get_process_complete_years()

        # get the latest year that has not had stats generated
        # year = [y for y in year_choices if y not in years]
        year.sort(reverse=True)
        print(year)

        # check if len of year > 0
        if len(year) > 0:

            # only use latest year
            for cat in stat_cats:
                status = gs.generate_stats2(year[0], cat)

                # these messages should be stored in /var/log/syslog
                # use cat syslog | grep CRON to view
                if status:
                    print("Generate Stats:", cat, "... Success")

                else:
                    print("Generate Stats:", cat, "... Failed")

            # run some tests
            status = aut.import_test_cases(year[0])

            if status:
                aut.run_test_cases('batting', year[0])
                # aut.run_test_cases('pitching', year[0])
                aut.run_test_cases('fielding', year[0])
            # else pass, as no test cases to run

            print("STATS GEN COMPLETE")
            return True

        else:
            print("No teams to generate stats for... Wait for next Year import.")
            return False
