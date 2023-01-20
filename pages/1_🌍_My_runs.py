import os
import streamlit as st
import altair as alt
from dataetl import files_to_dataframe

ACTIVITY_FOLDER = os.path.join(os.getcwd(), "runs")

runs = files_to_dataframe(ACTIVITY_FOLDER)

st.header("Calendar")
chart = alt.Chart(runs).mark_circle().encode(
    alt.X('week:O', title=""),
    alt.Y('day(date):O', scale=alt.Scale(domain=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']), title=""),
    size=alt.Size('sum(duration):Q', legend=None),
    color=alt.Color('effort:Q', legend=None))
st.altair_chart(chart, use_container_width=True)