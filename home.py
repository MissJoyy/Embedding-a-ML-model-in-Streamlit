import streamlit as st 
import requests
import json
from streamlit_lottie import st_lottie
from streamlit_extras.switch_page_button import switch_page
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader



st.set_page_config(
    page_title ='Home Page',
    page_icon ='🏠',
    layout="wide"
)


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

st.title("ChurnPredictor")
st.markdown("###### Your Go To Machine Learning Application To Predict Customer Churn Behavior")

if st.session_state["authentication_status"] is None:
    st.warning("Please Log in to get access to the application")
    test_code = '''
    Test 
    username: apaloojoy
    password: joy
    '''
    st.code(test_code)
        
elif st.session_state["authentication_status"] == False:
    st.error("Wrong username or password")
    st.info("Please Try Again")
    test_code = '''
    Test 
    username: apaloojoy
    password: joy
    '''
    st.code(test_code)
else:
    st.info("Login Successful")
    st.write(f'Welcome *{username}*')

    #logout user using streamlit authentication logout
    authenticator.logout('Logout', 'sidebar')


    


    #intro talking about title 
    with st.container():
       
    
        col1,col2 = st.columns(2)
        with col1:
            st.header("Key Features")
            st.write("""
                        - View Data - Allows you to view data 
                        - Predict - Feature that allows to make single prediction or predict your csv data in bulk
                        - View History - Allows you to view the history of your predictions
                        - Dashboard - View data visualizations
                        """)
            
        with col2:
            st.header("User Benefits")
            st.write("""
                        - Make data driven decisions effortlessly
                        - User-Friendly Interface
                        - Real-Time predictions
                        - Insightful dashboards
                        - Ease to use
                        """)
            
        col1,col2 = st.columns(2)
        with col1:
            st.header("Machine Learning Integration")
            st.write("""
                    - You have access to three trained machine learning models
                    - Simple integration and user-friendly access
                    - Save data to local database or locally for future use
                    - Get probability of predictions
                    """)
        with col2:
            st.header("How To Run Applicattion")
            code = '''
            #Activate Virtual Environment
            source venv/bin/activate

            #Install dependencies
            pip install -r requirements.txt

            #Run the application
            streamlit run home.py
            '''
            st.code(code,language="python")


            
            

     
            
            
            