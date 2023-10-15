import streamlit as st
import pandas as pd
from streamlit_authenticator import Authenticate
import yaml
from yaml import SafeLoader
import pandas as pd
import requests
# import re

# st.set_page_config(layout="wide")

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    authenticator.logout('Logout', 'main')
    x = requests.get('http://potholeapi.pythonanywhere.com/get_detections')
    df = pd.read_json(x.text)

    # df["city"] = df['city'].apply(lambda x: re.sub('[^A-Za-z0-9]+', '', x) if x is not None else x)
    # df["region"] = df['region'].apply(lambda x: re.sub('[^A-Za-z0-9]+', '', x))
    # df["country"] = df['country'].apply(lambda x: re.sub('[^A-Za-z0-9]+', '', x))

    st.title("Pothole Detection Admin Dashboard")
    country_filter = st.multiselect('Country Filter', df['country'].unique())
    df2 = df
    if country_filter:
        df2 = df2[df2['country'].isin(country_filter)]

    region_filter = st.multiselect('Region Filter', df2['region'].unique())
    if region_filter:
        df2 = df2[df2['region'].isin(region_filter)]

    city_filter = st.multiselect('City Filter', df2['city'].unique())
    if city_filter:
        df2 = df2[df2['city'].isin(city_filter)]

    # date filter
    df2.date = df2.date.map(lambda x: x.date())
    date_filter = st.date_input('Date Filter', [df2['date'].min(), df2['date'].max()])
    df2 = df2[(df2['date'] >= date_filter[0]) & (df2['date'] <= date_filter[1])]

    st.map(df2)
    
    st.header("Number of potholes per city")
    st.bar_chart(df.groupby('city')['nb_potholes'].sum())
    st.header("Number of potholes per region")
    st.bar_chart(df.groupby('region')['nb_potholes'].sum())
    st.header("Number of potholes per country")
    st.bar_chart(df.groupby('country')['nb_potholes'].sum())

elif authentication_status == False:
    st.error('Username/password is incorrect')
