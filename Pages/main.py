import streamlit as st 
from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import home, history, predict, dashboard, data

st.set_page_config(page_title='Churn Predictor')

# Class to handle multi-app functionality
class MultiApp:
    def __init__(self):  # Corrected the constructor
        self.apps = []

    def add_app(self, title, function):
        self.apps.append({
            'title': title,
            'function': function
        })

    def run(self):
        with st.sidebar:
            app = option_menu(
                menu_title='Churn Predictor',
                options=['Home', 'History', 'Predict', 'Data', 'Dashboard'],
                default_index=0
            )

        # Run the selected app's function
        if app == 'Home':
            home.app()
        elif app == 'History':
            history.app()
        elif app == 'Predict':
            predict.app()
        elif app == 'Data':
            data.app()
        elif app == 'Dashboard':
            dashboard.app()

# Initialize and run the app
app = MultiApp()
app.run()
