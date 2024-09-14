import streamlit as st 
import requests
import json
from streamlit_lottie import st_lottie
from streamlit_extras.switch_page_button import switch_page
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader



# Set up the page configuration
st.set_page_config(
    page_title="Churn Predictor",
    layout="wide",
    initial_sidebar_state="expanded"
)



# Load configuration from YAML file
try:
    with open('./config.yaml', 'r', encoding='utf-8') as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("Configuration file not found.")
    st.stop()
except yaml.YAMLError as e:
    st.error(f"Error loading YAML file: {e}")

    st.stop()

# Hashing all plain text passwords once
# Hasher.hash_passwords(config['credentials'])

# Creating the authenticator object and storing it in session state
if 'authenticator' not in st.session_state:
    st.session_state['authenticator'] = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['pre-authorized']
        # False
    )

authenticator = st.session_state['authenticator']

# Login page content
if not st.session_state.get("authentication_status"):
    st.write("---")
    st.title(" 🔐 Welcome to the Login Page")
    left_column, right_column = st.columns(2)

    with left_column:
        st.header("Secure Login")
        st.write(
            """
            Please enter your credentials to access your account.
            Your information is safe with us, and we ensure top-notch security.
            """
        )
        st.subheader("About the Churn Predictor App")
        st.write(
            """
            The Churn Predictor app is designed to analyze customer data and predict churn risk. 
            It helps businesses identify customers who are likely to leave and take proactive measures to retain them.
            """
        )

    

try:
    authenticator.login()
except LoginError as e:
    st.error(e)

if st.session_state.get("authentication_status"):
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f'Welcome *{st.session_state["name"]}*')

    home_page = st.Page(
        page="pages/00_Home.py",
        title="Home",
        icon="🏡",
        default=True
    )

    

    data_page = st.Page(
        page="pages/04_Data.py",
        title="Data Overview",
        icon="📊"
    )

    dashboard_page = st.Page(
        page="pages/01_Dashboard.py",
        title="Analytics Dashboard",
        icon="📈"
    )

    history_page = st.Page(
        page="pages/02_History.py",
        title="Historical Insights",
        icon="🕰️"
    )

    prediction_page = st.Page(
        page="pages/03_predict.py",
        title="Future Projections",
        icon="🔮"
    )

    # Show authenticated pages
    pg = st.navigation(
        {
            "User Interaction": [home_page],
            "Data Management": [data_page, dashboard_page],
            "Insights and Forecasting": [history_page, prediction_page],
        }
    )

    # --- NAVIGATION RUN ---
    pg.run()

elif st.session_state.get("authentication_status") is False:
    st.error('Username/password is incorrect')
elif st.session_state.get("authentication_status") is None:
    st.warning('Please enter your username and password')