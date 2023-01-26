import streamlit as st
from utils import decimal_to_time, week_to_dates, month_to_dates

format_dict = {
    "week": week_to_dates,
    "month": month_to_dates,
    "year": lambda x: x
}

def get_runs_stat(df, time, unit):
    if time == df[unit].min():
        runs_delta = None
    else:
        runs_delta = int(df[df[unit] == time].start.item() - df[df[unit] == time - 1].start.item())
        sign = "+" if runs_delta >= 0 else ""
        runs_delta = f'{sign}{runs_delta}'
    runs = df[df[unit] == time].start
    return runs,runs_delta,"normal"

def get_distance_stat(df, time, unit):
    if time == df[unit].min():
        distance_delta = None
    else:
        kilometers_delta = df[df[unit] == time].distance.item() - df[df[unit] == time - 1].distance.item()
        sign = "+" if kilometers_delta >= 0 else ""
        distance_delta = f'{sign}{round(kilometers_delta,2)} km'
    distance = df[df[unit] == time].distance.round(2)
    return distance, distance_delta,"normal"

def get_pace_stat(df, time, unit):
    if time == df[unit].min():
        pace_delta = None
    else:
        pace_delta = df[df[unit] == time].pace.item() - df[df[unit] == time - 1].pace.item()
        sign = "+" if pace_delta >= 0 else "-"
        hd, md, sd = decimal_to_time(abs(pace_delta))
        pace_delta = "%s%d'%02d\"" % (sign, md, sd)
    h, m, s = decimal_to_time(df[df[unit] == time].pace)
    pace = "%d'%02d\"" % (m, s)
    return pace, pace_delta, "inverse"

def get_duration_stat(df, time, unit):
    if time == df[unit].min():
        duration_delta = None
    else:
        duration_delta = df[df[unit] == time].duration.item() - df[df[unit] == time - 1].duration.mean()
        sign = "+" if duration_delta >= 0 else "-"
        hd, md, sd = decimal_to_time(abs(duration_delta))
        duration_delta = "%s%d:%02d:%02d" % (sign, hd, md, sd)
    h, m, s = decimal_to_time(df[df[unit] == time].duration)
    duration = "%d:%02d:%02d" % (h, m, s)
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
    options = [*reversed(range(df[unit].min(), df[unit].max()+1))]
    nb = min(7,len(options))
    return options[:nb]

def display_metrics(df, unit):
    #Get the running metrics per time unit
    df_agg = df.groupby([unit], as_index=False).agg({'start': 'count', 'distance': 'sum', 'duration': 'sum'})
    df_agg['pace'] = df_agg.duration / df_agg.distance

    #Let the user choose which time to display
    options = get_options(df, unit)
    option = st.selectbox(unit, options, index=0, format_func=format_dict[unit], label_visibility="collapsed")

    metrics = ['Runs', 'Kilometers', 'Pace', 'Time']
    cols = st.columns(len(metrics))

    for i in range(len(cols)):
        metric, delta, direction = get_metrics(df_agg, metrics[i], option, unit)
        cols[i].metric(metrics[i], metric, delta, direction)

    return option