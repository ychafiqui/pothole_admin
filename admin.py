import streamlit as st
import pandas as pd
from streamlit_authenticator import Authenticate
import yaml
from yaml import SafeLoader
import pandas as pd

if not hasattr(st, 'already_started_server'):
    # Hack the fact that Python modules (like st) only load once to
    # keep track of whether this file already ran.
    st.already_started_server = True

    st.write('''
        The first time this script executes it will run forever because it's
        running a Flask server.

        Just close this browser tab and open a new one to see your Streamlit
        app.
    ''')

    from flask import Flask,request

    app = Flask(__name__)

    @app.route('/get_detections')
    def get_detections():
        df = pd.read_csv("detections/detections.csv")
        json_data = df.to_json(orient='records')
        return json_data

    @app.route('/add_detections', methods=['POST'])
    def add_detections():
        image = request.form['image']
        lat = request.form['lat']
        lon = request.form['lon']
        nb_potholes = request.form['nb_potholes']
        date = request.form['date']
        city = request.form['city']
        region = request.form['region']
        country = request.form['country']
        df = pd.read_csv("detections/detections.csv")
        df = pd.concat([df, pd.DataFrame({'image': [image], 'lat': [lat], 'lon': [lon], 'nb_potholes': [nb_potholes], 'date': [date], 'city': [city], 'region': [region], 'country': [country]})], ignore_index=True)
        df.to_csv("detections/detections.csv", index=False)
        json_data = df.to_json(orient='records')
        return json_data

    app.run()

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
    df = pd.read_csv("detections/detections.csv")
    st.map(df)
elif authentication_status == False:
    st.error('Username/password is incorrect')