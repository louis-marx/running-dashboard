import os
import json
import requests
import datetime
import streamlit as st
import numpy as np
import pandas as pd

ACTIVITY_FOLDER = os.path.join(os.getcwd(), "runs")
ACTIVITY_LIST_URL = "https://api.nike.com/sport/v3/me/activities/after_time/0"
ACTIVITY_LIST_PAGINATION = "https://api.nike.com/sport/v3/me/activities/after_id/{after_id}"
ACTIVITY_DETAILS_URL = "https://api.nike.com/sport/v3/me/activity/{activity_id}?metrics=ALL"

st.title("My running dashboard")

with st.form("my_form"):
    access_token = st.text_input('Access Token', placeholder='eyJhbGc...')
    submitted = st.form_submit_button("Submit")
    headers = {'Authorization' : 'Bearer ' + access_token}

@st.cache(suppress_st_warning=True)
def load_data():
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

load_data()

dir_list = os.listdir(ACTIVITY_FOLDER)
if ".DS_Store" in dir_list:
     dir_list.remove(".DS_Store")
runs = []

for file in dir_list:

     data = json.load(open(ACTIVITY_FOLDER+"/"+file))

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
runs.loc[(runs.program_type == 'Long run') | runs.name.str.contains('Gratification'), 'type'] = 'longrun'
runs.loc[runs.type == '', 'type'] = 'recoveryrun'

runs['date'] = runs.start.dt.date
runs['week'] = runs.start.dt.isocalendar().year * 100 + runs.start.dt.isocalendar().week
runs['weekday'] = runs.start.dt.strftime('%A')
runs['month'] = runs.start.dt.month
runs['steps_per_minute'] = runs.steps / runs.duration
runs['stride_length'] = 1000 * runs.distance / runs.steps

# idx = pd.date_range(runs['date'].min() - datetime.timedelta(days=runs['date'].min().weekday()), datetime.datetime.now() + datetime.timedelta(days=(6 - datetime.datetime.now().weekday())))
# for date in idx[~idx.isin(runs['date'])]:
#     norun = pd.DataFrame(np.nan, index=[0], columns=runs.columns)
#     norun['date'] = date.date()
#     norun['week'] = date.isocalendar().week
#     norun['weekday'] = date.strftime('%A')
#     runs = pd.concat([runs, norun], ignore_index=True)

runs = runs.sort_values(by=['date'], ignore_index=True)

average_pace = runs[['week', 'distance']].groupby(['week'], as_index=False).sum()

st.subheader("Distance per week")
st.bar_chart(average_pace, x="week", y="distance")