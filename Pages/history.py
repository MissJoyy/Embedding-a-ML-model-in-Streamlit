import os
import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def app():
    st.write('History Page 🕰️')

    #### User Authentication
    # load the config.yaml file 
    with open('./config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Create an authentication object
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['pre-authorized']
    )
    # invoke the login authentication
    name, authentication_status, username = authenticator.login(location="sidebar")

    if authentication_status is None:
        st.warning("Please Log in to get access to the application")
        test_code = '''
        Test Account
        username: apaloo
        password: 1234
        '''
        st.code(test_code)
            
    elif authentication_status == False:
        st.error("Wrong username or password")
        st.info("Please Try Again")
        test_code = '''
        Test Account
        username: apaloojoy
        password: 1234
        '''
        st.code(test_code)

    else:
        #logout user using streamlit authentication logout
        authenticator.logout('Logout', 'sidebar')

        def display_history_page():
            # get the path of the history data
            csv_path = "./data/prediction_history.csv"
            csv_exists = os.path.exists(csv_path)

            if csv_exists:
                history_data = pd.read_csv(csv_path)
                st.dataframe(history_data)
            else:
                st.write("No history data found")
                st.write("Please run the app and make a prediction to view the history page")
                st.stop()

        display_history_page()


