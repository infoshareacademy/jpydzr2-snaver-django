def prev_month(date):
    if date.month > 1:
        return date.replace(month=date.month-1, day=1)
    else:
        return date.replace(year=date.year-1, month=12, day=1)


def next_month(date):
    if date.month < 12:
        return date.replace(month=date.month+1, day=1)
    else:
        return date.replace(year=date.year+1, month=1, day=1)
