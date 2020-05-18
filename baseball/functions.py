# custom functions listed in this file
import datetime
from .oper import check_latest_imports as chk
from .forms import GetYear, ProcessTeam, GenerateStats
from django.db import models
# from .models import JobRequirements


# instantiate forms
def instantiate_forms():

    year_choices = chk.get_year_choices()[1]
    form_import = GetYear(year_choices, initial={'form_type': 'import_year'})
    year_choices = chk.get_team_choices('process_team')[1]
    team_choices = chk.get_team_choices('process_team')[3]
    form_process = ProcessTeam(year_choices, team_choices, initial={'form_type': 'process_team'})
    year_choices = chk.get_team_choices('generate_stats')[1]
    team_choices = chk.get_team_choices('generate_stats')[3]
    form_gen_stats = GenerateStats(year_choices, team_choices, initial={'form_type': 'generate_stats'})

    the_forms = [form_import, form_process, form_gen_stats]

    return the_forms
