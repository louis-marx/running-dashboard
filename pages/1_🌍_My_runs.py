import os
import streamlit as st
import altair as alt
from dataetl import files_to_dataframe
from utils import decimal_to_time

ACTIVITY_FOLDER = os.path.join(os.getcwd(), "runs")

runs = files_to_dataframe(ACTIVITY_FOLDER)

st.title('My running log')

st.header("Calendar")
chart = alt.Chart(runs).mark_circle().encode(
    alt.X('week:O', title=""),
    alt.Y('day(date):O', scale=alt.Scale(domain=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']), title=""),
    size=alt.Size('sum(duration):Q', legend=None),
    color=alt.Color('effort:Q', legend=None))
st.altair_chart(chart, use_container_width=True)

st.header("Running Log")
st.markdown("---")

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

runs = runs.sort_values(by=['date'], ascending=False, ignore_index=True)
for index, row in runs.iterrows():
    # title, program = st.columns(2)
    # with title:
    #     st.markdown(f"### {row['name']}")
    # with program:
    #     st.info(row.program_name + " Training Plan")
    st.info(row.program_name + " Training Plan")
    st.markdown(f"### {row.date.strftime('%d %B %Y')} - :blue[{row['name']}]")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Kilometers",round(row.distance,2))
        st.metric("Weather",get_weather_icon(row.weather))
    with col2:
        h, m, s = decimal_to_time(row.pace)
        pace = "%d'%02d\"" % (m, s)
        st.metric("Pace",pace)
        st.metric("Temperature", f'{round(row.temperature)}°C')
    with col3:
        h, m, s = decimal_to_time(row.duration)
        duration = "%d:%02d:%02d" % (h, m, s)
        st.metric("Time",duration)
        st.metric("SPM", round(row.steps_per_minute))
    st.markdown("---")