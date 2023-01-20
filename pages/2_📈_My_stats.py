# Import modules
import os
import datetime as dt
import streamlit as st
import numpy as np
import pandas as pd 
import altair as alt
from utils import decimal_to_time, week_to_dates, month_to_dates
from nikeapi import nike_api_call
from dataetl import files_to_dataframe
from metrics import display_metrics
from charts import display_charts

ACTIVITY_FOLDER = os.path.join(os.getcwd(), "runs")

st.set_page_config(
    page_title="Nike Run Dashboard",
    page_icon=":runner:",
)

#Display dashboard
st.title("My running dashboard")

runs = files_to_dataframe(ACTIVITY_FOLDER)

st.subheader("Activity")
timeUnits = ["Week", "Month", "Year"]
tabs = st.tabs(timeUnits)

for i in range(len(tabs)):
    with tabs[i]:
        option = display_metrics(runs, timeUnits[i].lower())
        display_charts(runs, option, timeUnits[i].lower())