import streamlit as st

st.title('Home Page')

with st.sidebar:

    st.markdown("# Get your latest data")
    with st.form("access_token"):
        access_token = st.text_input('Enter your Nike access token', placeholder='eyJhbGc...')

        submitted = st.form_submit_button("Call the API", type='primary')
        if submitted:
            headers = {'Authorization' : 'Bearer ' + access_token}
            nike_api_call(headers)