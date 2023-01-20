import datetime as dt

def decimal_to_time(timedelta):
    hours = int(timedelta) // 60
    minutes = int(timedelta % 60)
    seconds = int((timedelta*60) % 60)
    return hours, minutes, seconds

def week_to_dates(option):
    active_week = (dt.date.today().isocalendar()[1]+13)%52
    if option == active_week:
        week_date = "This Week"
    elif option == active_week - 1:
        week_date = "Last Week"
    else:
        year = 2022 + (option+38) // 52
        week = 1 + (option+38) % 52
        mon_date = dt.datetime.fromisocalendar(year, week, 1).strftime("%d/%m")
        sun_date = dt.datetime.fromisocalendar(year, week, 7).strftime("%d/%m")
        week_date = f'{mon_date}-{sun_date}'
    return week_date

def month_to_dates(option):
    month = dt.date(2022 + (option+8) // 12, 1 + (option+8) % 12, 1).strftime("%B %Y")
    return month