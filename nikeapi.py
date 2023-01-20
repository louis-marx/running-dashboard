import os
import json
import requests
import streamlit as st

# Define constants
ACTIVITY_FOLDER = os.path.join(os.getcwd(), "runs")
ACTIVITY_LIST_URL = "https://api.nike.com/sport/v3/me/activities/after_time/0"
ACTIVITY_LIST_PAGINATION = "https://api.nike.com/sport/v3/me/activities/after_id/{after_id}"
ACTIVITY_DETAILS_URL = "https://api.nike.com/sport/v3/me/activity/{activity_id}?metrics=ALL"

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
    
    st.success('Running data successfully imported')
    st.balloons()
    return None