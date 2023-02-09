import streamlit as st
import datetime as dt
import math
from utils import decimal_to_time, week_to_dates, month_to_dates

format_dict = {
    "week": week_to_dates,
    "month": month_to_dates,
    "year": lambda x: x
}

def get_runs_stat(df, time, unit):
    runs = len(df[df[unit] == time])
    runs_delta = len(df[df[unit] == time]) - len(df[df[unit] == time-1])
    sign = "+" if runs_delta >= 0 else ""
    runs_delta = f'{sign}{runs_delta}'
    return runs, runs_delta, "normal"

def get_distance_stat(df, time, unit):
    distance = df[df[unit] == time].distance.sum().round(2)
    distance_delta = df[df[unit] == time].distance.sum() - df[df[unit] == time - 1].distance.sum()
    sign = "+" if distance_delta >= 0 else ""
    distance_delta = f'{sign}{round(distance_delta,2)} km'
    return distance, distance_delta, "normal"

def get_pace_stat(df, time, unit):
    current_pace = df[df[unit] == time].duration.sum()/df[df[unit] == time].distance.sum()
    previous_pace = df[df[unit] == time-1].duration.sum()/df[df[unit] == time-1].distance.sum()
    if not(math.isnan(current_pace)):
        h, m, s = decimal_to_time(current_pace)
        pace = "%d'%02d\"" % (m, s)
        if not(math.isnan(previous_pace)):
            pace_delta = current_pace - previous_pace
            sign = "+" if pace_delta >= 0 else "-"
            hd, md, sd = decimal_to_time(abs(pace_delta))
            pace_delta = "%s%d'%02d\"" % (sign, md, sd)
        else:
            pace_delta = None
    else:
        pace = "-'--\""
        pace_delta = None
    return pace, pace_delta, "inverse"

def get_duration_stat(df, time, unit):
    h, m, s = decimal_to_time(df[df[unit] == time].duration.sum())
    duration = "%d:%02d:%02d" % (h, m, s)
    duration_delta = df[df[unit] == time].duration.sum() - df[df[unit] == time - 1].duration.sum()
    sign = "+" if duration_delta >= 0 else "-"
    hd, md, sd = decimal_to_time(abs(duration_delta))
    duration_delta = "%s%d:%02d:%02d" % (sign, hd, md, sd)
    return duration, duration_delta, "normal"

def get_metrics(df, metric, time, unit):
    if metric  == "Runs":
        return get_runs_stat(df, time, unit)
    elif metric == "Kilometers":
        return get_distance_stat(df, time, unit)
    elif metric == "Pace":
        return get_pace_stat(df, time, unit)
    elif metric == "Time":
        return get_duration_stat(df, time, unit)
    else:
        return None

def get_options(df, unit):
    if unit == 'week':
        options = [*reversed(range(df[unit].min(), (dt.date.today().isocalendar()[1]+13)%52+1))]
    elif unit == 'month':
        options = [*reversed(range(df[unit].min(), (dt.date.today().month+15)%12+1))]
    elif unit == 'year':
        options = [*reversed(range(df[unit].min(), dt.date.today().year+1))]
    nb = min(7,len(options))
    return options[:nb]

def display_metrics(df, unit):
    #Get the running metrics per time unit
    # df_agg = df.groupby([unit], as_index=False).agg({'start': 'count', 'distance': 'sum', 'duration': 'sum'})
    # df_agg['pace'] = df_agg.duration / df_agg.distance

    #Let the user choose which time to display
    options = get_options(df, unit)
    option = st.selectbox(unit, options, index=0, format_func=format_dict[unit], label_visibility="collapsed")

    metrics = ['Runs', 'Kilometers', 'Pace', 'Time']
    cols = st.columns(len(metrics))

    for i in range(len(cols)):
        metric, delta, direction = get_metrics(df, metrics[i], option, unit)
        cols[i].metric(metrics[i], metric, delta, direction)

    return option