# libraries


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
