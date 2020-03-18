# libraries
import datetime


# performance time conversions
def seconds_convert(total_time):

    hours = 0
    minutes = 0
    out_str = ''

    # hours
    if total_time > 60*60:
        hours = total_time // 60*60
        out_str = str(int(hours)) + ' hours, '

    # minutes
    if total_time > 60:
        minutes = (total_time - hours*60*60) // 60
        out_str = out_str + str(int(minutes)) + ' minutes, and '

    # seconds
    seconds = total_time - hours*60*60 - minutes*60
    out_str = out_str + str(round(seconds, 5)) + ' seconds.'

    return out_str


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
