# libraries


# performance time conversions
def seconds_convert(total_time):

    hours = 0
    minutes = 0
    seconds = 0
    out_str = ''

    # hours
    if total_time > 60*60:
        hours = total_time // 60*60
        out_str = hours + ' hours, '

    # minutes
    if total_time > 60:
        minutes = (total_time - hours*60*60) // 60
        out_str = out_str + minutes + ' minutes, and '

    # seconds
    seconds = total_time - hours*60*60 - minutes*60
    out_str = out_str + seconds + ' seconds.'

    return out_str
