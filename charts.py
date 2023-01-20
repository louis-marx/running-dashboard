import calendar
import streamlit as st
import altair as alt

def get_specs(time, unit):
    if unit == 'week':
        return {'domain': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                'timeUnit': 'day'}
    elif unit == 'month':
        return {'domain': [*range(1, calendar.monthrange(2022 + (time+8) // 12, 1 + (time+8) % 12)[1] + 1)],
                'timeUnit': 'date' }
    elif unit == 'year':
        return {'domain': ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
                'timeUnit': 'month' }
    else:
        return None

def display_charts(df, time, unit):
    # Display a chart of distance ran over the time period
    specs = get_specs(time, unit)
    st.subheader("Distance")
    chart = alt.Chart(df[df[unit] == time]).mark_bar().encode(
        alt.X('date', scale=alt.Scale(domain=specs['domain']), title="", timeUnit=specs['timeUnit'], type='ordinal'), 
        alt.Y('distance', title="", type='quantitative'))
    st.altair_chart(chart, use_container_width=True)

    # Display a chart of distance ran over the time period
    # specs = get_specs(time, unit)
    # st.subheader("Pace")
    # chart = alt.Chart(df[df[unit] == time]).mark_bar().encode(
    #     alt.X('date', scale=alt.Scale(domain=specs['domain']), title="", timeUnit=specs['timeUnit'], type='ordinal'), 
    #     alt.Y('mean(pace)', title="", type='quantitative'))
    # st.altair_chart(chart, use_container_width=True)

    return None