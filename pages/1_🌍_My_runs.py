import os
import datetime as dt
import streamlit as st
import altair as alt
import urllib.request
from PIL import Image
from dataetl import files_to_dataframe
from utils import decimal_to_time

ACTIVITY_FOLDER = os.path.join(os.getcwd(), "runs")

st.set_page_config(
    page_title="Nike Run Dashboard",
    page_icon=":runner:"
)

runs = files_to_dataframe(ACTIVITY_FOLDER)

st.title('My running log')

st.header("Calendar")
chart = alt.Chart(runs).mark_circle().encode(
    alt.X('week:O', title=""),
    alt.Y('day(date):O', scale=alt.Scale(domain=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']), title=""),
    size=alt.Size('duration:Q', legend=None),
    color=alt.Color('effort:Q', legend=None))
st.altair_chart(chart, use_container_width=True)

st.header("Running Log")

def get_weather_icon(weather):
    if weather == "rain":
        icon = '🌧️'
    elif weather == "partly-cloudy-day":
        icon = '🌤'
    elif weather == "partly-cloudy-night":
        icon = '🌙'
    elif weather == "cloudy":
        icon  = '☁'
    elif weather == "wind":
        icon = '🌬'
    elif weather == 'clear-night':
        icon = '🌙'
    elif weather == 'clear-day':
        icon = '☀️'
    else:
        icon = weather
    return icon

# d = st.date_input(
#     "Choose a specific date",
#     runs.date.min())

runs = runs.sort_values(by=['date'], ascending=False, ignore_index=True)
for index, row in runs.iterrows():
    st.markdown("---")
    if row.program_name != '':
        st.info(row.program_name + " Training Plan")
    img, ttl = st.columns([2, 7], gap="medium")
    with img:
        urllib.request.urlretrieve(row['thumbnail'], "image.jpg")
        image = Image.open('image.jpg')
        st.image(image, use_column_width=True)
    with ttl:
        st.markdown(f"### {row.date.strftime('%d/%m/%Y')}")
        st.markdown(f"### :blue[{row['name']}]")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Kilometers",round(row.distance,2))
        # st.metric("Weather",get_weather_icon(row.weather))
    with col2:
        h, m, s = decimal_to_time(row.pace)
        pace = "%d'%02d\"" % (m, s)
        st.metric("Pace",pace)
        # st.metric("Temperature", f'{round(row.temperature)}°C')
    with col3:
        h, m, s = decimal_to_time(row.duration)
        duration = "%d:%02d:%02d" % (h, m, s)
        st.metric("Time",duration)
    with col4:
        st.metric("SPM", round(row.steps_per_minute))
