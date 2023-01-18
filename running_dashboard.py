# Import modules
import os
import json
import requests
import datetime as dt
import streamlit as st
import numpy as np
import pandas as pd 
import altair as alt

# Define constants
ACTIVITY_FOLDER = os.path.join(os.getcwd(), "runs")
ACTIVITY_LIST_URL = "https://api.nike.com/sport/v3/me/activities/after_time/0"
ACTIVITY_LIST_PAGINATION = "https://api.nike.com/sport/v3/me/activities/after_id/{after_id}"
ACTIVITY_DETAILS_URL = "https://api.nike.com/sport/v3/me/activity/{activity_id}?metrics=ALL"

#Define functions
def nike_api_call(headers):
    activity_ids = []
    page_num = 1
    next_page = ACTIVITY_LIST_URL
    while True:
        activity_list = requests.get(next_page, headers=headers)
        for activity in activity_list.json()["activities"]:
            if (
                activity["type"] == "run"
                and activity.get("tags", {}).get("com.nike.running.runtype", "") != "manual"
            ):
                activity_ids.append(activity.get("id"))

        if activity_list.json()["paging"].get("after_id"):
            page_num += 1
            next_page = ACTIVITY_LIST_PAGINATION.format(
                after_id=activity_list.json()["paging"]["after_id"]
            )
            continue
        break

    if not os.path.exists(ACTIVITY_FOLDER):
            os.mkdir(ACTIVITY_FOLDER)

    i=0.0
    my_bar = st.progress(i)
    for activity in activity_ids:
        html = requests.get(
            ACTIVITY_DETAILS_URL.format(activity_id=activity), headers=headers
        )
        activity_details = html.json()
        title = activity_details.get("tags", {}).get("com.nike.name", "")
        json_path = os.path.join(ACTIVITY_FOLDER, f"{activity}.json")
        with open(json_path, "w") as f:
            f.write(json.dumps(activity_details))
        i+=1
        my_bar.progress(i/len(activity_ids))
    return None

def files_to_dataframe(folder):
    dir_list = os.listdir(folder)
    if ".DS_Store" in dir_list:
        dir_list.remove(".DS_Store")

    runs = []
    for file in dir_list:
        data = json.load(open(folder+"/"+file))
        run = [str(data['tags']['com.nike.name']),
                int(data['start_epoch_ms']),
                int(data['end_epoch_ms']),
                int(data['active_duration_ms']),
                str(data['tags']['com.nike.running.goaltype']),
                float(data['tags']['com.nike.temperature']),
                str(data['tags']['com.nike.weather']),
                int(data['tags']['rpe']),
                str(data['tags']['terrain'])]
            
        if 'com.nike.nrc.program.workout.title' in data['tags']:
            run.append(str(data['tags']['com.nike.nrc.program.workout.title']))
        else:
            run.append('')
        
        if 'com.nike.nrc.program.title' in data['tags']:
            run.append(str(data['tags']['com.nike.nrc.program.title']))
        else:
            run.append('')

        summary = pd.DataFrame(data['summaries'])
        summary.sort_values("metric", inplace=True)
        summary = summary[summary.metric != "nikefuel"]["value"].tolist()
        runs.append(run+summary)

    runs = pd.DataFrame(runs, columns = ['name', 'start', 'end', 'duration', 'goaltype', 'temperature', 'weather', 'effort', 'terrrain', 'program_type', 'program_name', 'ascent', 'calories', 'descent', 'distance', 'pace', 'speed', 'steps'])
    runs.start = pd.to_datetime(runs.start, unit='ms')
    runs.end = pd.to_datetime(runs.end, unit='ms')
    runs.duration = runs.duration / 60000

    runs['type'] = ''
    runs.loc[runs.goaltype.str.contains('speed'), 'type'] = 'speedrun'
    runs.loc[(runs.program_type.str.casefold() == 'long run') | runs.name.str.contains('Gratification'), 'type'] = 'longrun'
    runs.loc[runs.type == '', 'type'] = 'recoveryrun'

    runs['date'] = runs.start.dt.date
    runs['week'] = 100 * runs.start.dt.isocalendar().year + runs.start.dt.isocalendar().week 
    runs['weekday'] = runs.start.dt.strftime('%A')
    runs['month'] = runs.start.dt.month
    runs['steps_per_minute'] = runs.steps / runs.duration
    runs['stride_length'] = 1000 * runs.distance / runs.steps

    idx = pd.date_range(runs['date'].min() - dt.timedelta(days=runs['date'].min().weekday()), dt.datetime.now() + dt.timedelta(days=(6 - dt.datetime.now().weekday())))
    for date in idx[~idx.isin(runs['date'])]:
        norun = pd.DataFrame(np.nan, index=[0], columns=runs.columns)
        norun['distance'] = 0
        norun['date'] = date.date()
        norun['week'] = 100*date.isocalendar()[0]+date.isocalendar()[1]
        norun['weekday'] = date.strftime('%A')
        runs = pd.concat([runs, norun], ignore_index=True)

    runs = runs.sort_values(by=['date'], ignore_index=True)
    return runs

def decimal_to_time(timedelta):
    hours = int(timedelta) // 60
    minutes = int(timedelta % 60)
    seconds = int((timedelta*60) % 60)
    return hours, minutes, seconds

def week_to_dates(option):
    active_week = 100 * dt.date.today().isocalendar()[0] + dt.date.today().isocalendar()[1]
    if option == active_week:
        week_date = "This Week"
    elif option == active_week - 1:
        week_date = "Last Week"
    else:
        year = option // 100
        week = option % 100
        mon_date = dt.datetime.fromisocalendar(year, week, 1).strftime("%d/%m")
        sun_date = dt.datetime.fromisocalendar(year, week, 7).strftime("%d/%m")
        week_date = f'{mon_date}-{sun_date}'
    return week_date

#Display dashboard
st.title("My running dashboard")

with st.sidebar:
    st.info("Get the latest data by calling the Nike API")
    with st.form("access_token"):
        access_token = st.text_input('Enter your access token', placeholder='eyJhbGc...')

        submitted = st.form_submit_button("Call the API")
        if submitted:
            headers = {'Authorization' : 'Bearer ' + access_token}
            nike_api_call(headers)

runs = files_to_dataframe(ACTIVITY_FOLDER)

st.subheader("Activity")
tab1, tab2, tab3, tab4 = st.tabs(["Week", "Month", "Year", "All"])


with tab1:
    #Get the running metrics per week
    runs_week_agg = runs.groupby(['week'], as_index=False).agg({'start': 'count', 'distance': 'sum', 'duration': 'sum'})
    runs_week_agg['pace'] = runs_week_agg.duration / runs_week_agg.distance

    #Let the user choose which week to display
    option = st.selectbox('Week',runs.week.unique(), index=len(runs.week.unique())-1, format_func=week_to_dates, label_visibility="collapsed")

    col1, col2, col3, col4 = st.columns(4)

    #Display the number of runs
    if option == runs_week_agg.week.min():
        delta = None
    else:
        runs_delta = int(runs_week_agg[runs_week_agg.week == option].start.item() - runs_week_agg[runs_week_agg.week == option - 1].start.item())
        sign = "+" if runs_delta >= 0 else ""
        delta = f'{sign}{runs_delta}'
    col1.metric("Runs", runs_week_agg[runs_week_agg.week == option].start, delta)

    #Display the number of kilometers ran
    if option == runs_week_agg.week.min():
        delta = None
    else:
        kilometers_delta = runs_week_agg[runs_week_agg.week == option].distance.item() - runs_week_agg[runs_week_agg.week == option - 1].distance.mean()
        sign = "+" if kilometers_delta >= 0 else ""
        delta = f'{sign}{round(kilometers_delta,2)} km'
    col2.metric("Kilometers", runs_week_agg[runs_week_agg.week == option].distance.round(2), delta)

    #Display the average pace
    if option == runs_week_agg.week.min():
        delta = None
    else:
        pace_delta = runs_week_agg[runs_week_agg.week == option].pace.item() - runs_week_agg[runs_week_agg.week == option - 1].pace.mean()
        sign = "+" if pace_delta >= 0 else "-"
        hd, md, sd = decimal_to_time(abs(pace_delta))
        delta = "%s%d'%02d\"" % (sign, md, sd)
    pace = runs_week_agg[runs_week_agg.week == option].pace
    h, m, s = decimal_to_time(pace)
    col3.metric("Pace", "%d'%02d\"" % (m, s), delta, "inverse")

    #Display the time ran
    if option == runs_week_agg.week.min():
        delta = None
    else:
        time_delta = runs_week_agg[runs_week_agg.week == option].duration.item() - runs_week_agg[runs_week_agg.week == option - 1].duration.mean()
        sign = "+" if time_delta >= 0 else "-"
        hd, md, sd = decimal_to_time(abs(time_delta))
        delta = "%s%d:%02d:%02d" % (sign, hd, md, sd)
    time = runs_week_agg[runs_week_agg.week == option].duration
    h, m, s = decimal_to_time(time)
    col4.metric("Time", "%d:%02d:%02d" % (h, m, s), delta)

    #Display a chart of distance ran over the week
    st.subheader("Distance")
    chart = alt.Chart(runs[runs.week == option]).mark_bar().encode(
        alt.X('date', sort=["Mon"], timeUnit="day", title="", type='ordinal'), 
        alt.Y('distance', title="", type='quantitative'))
    st.altair_chart(chart, use_container_width=True)

with tab2:
    #Get the running metrics per month
    runs_month_agg = runs.groupby(['month'], as_index=False).agg({'start': 'count', 'distance': 'sum', 'duration': 'sum'})
    runs_month_agg['pace'] = runs_month_agg.duration / runs_month_agg.distance

    #Let the user choose which week to display
    option = st.selectbox('Month',runs.month.unique())

with tab3:
    average_pace = runs[['week', 'distance']].groupby(['week'], as_index=False).sum()
    st.bar_chart(average_pace, x="week", y="distance")