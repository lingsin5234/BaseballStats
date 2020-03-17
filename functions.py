# custom functions listed in this file
import datetime
from django.db import models
# from .models import JobRequirements


# generate the years
def gen_year():
    mlb_start_year = 1918
    now = datetime.datetime.now()
    tuple_years = []
    for y in range(now.year - mlb_start_year):
        yr = (mlb_start_year + y, mlb_start_year + y)
        tuple_years.insert(0, yr)  # want to add to beginning of list

    # print(tuple_years)
    return tuple_years


# show year choices
def show_year_choices():
    # year_choices = [(c.year, c.year) for c in JobRequirements.objects.filter(form_type='import_year')]
    all_years = gen_year()
    # if year_choices in all_years:
    #     return all_years
    # else:
    return "Did not work."
