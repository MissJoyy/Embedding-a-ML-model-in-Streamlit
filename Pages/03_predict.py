import os
import streamlit as st
import pandas as pd
import joblib
import datetime
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

st.set_page_config(
    page_title ='Predict Page',
    page_icon ='🤖',
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

if st.session_state["authentication_status"] is None:
    st.warning("Please Log in to get access to the application")
    test_code = '''
    Test Account
    username: joyapaloo
    password: 1234
    '''
    st.code(test_code)
        
elif st.session_state["authentication_status"] == False:
    st.error("Wrong username or password")
    st.info("Please Try Again")
    test_code = '''
    Test Account
    username: joyapaloo
    password: 1234
    '''
    st.code(test_code)
else:
    #logout user using streamlit authentication logout
    authenticator.logout('Logout', 'sidebar')


    st.title("Predict Churn 🤖!")
    # load the machine learning model
    @st.cache_resource()
    def load_ml_components():
        with open("./models/best_models.joblib","rb") as file:
            model_components = joblib.load(file)
        return model_components

    model_components = load_ml_components()

    # load model components
    catboost_model = model_components["catboost_model"]
    logistic_regressor = model_components["log_regression"]
    sgb_classifier = model_components["sgb_classifier"]

    # initialize the session state

    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "Catboost" 
    # select a model to use
    col1,col2 = st.columns(2)
    with col1:
        selected_model = st.selectbox("Select model to predict",
                                                    options=["Catboost","Logistic Regression","SGB"],
                                                    key="selected_model",
                                                    index=["Catboost","Logistic Regression","SGB"].index(st.session_state.selected_model))
    st.write("#")
    # Update the session state based on the selected model
    selected_model = st.session_state.selected_model


    # select a model from the select_box
    @st.cache_resource(show_spinner="loading models...")
    def get_selected_model(selected_model):
        if selected_model == "Catboost":
            pipeline =  catboost_model
        elif selected_model == "Logistic Regression":
            pipeline =  logistic_regressor
        else:
            pipeline =  sgb_classifier

        encoder = model_components["encoder"]
        return pipeline, encoder


    # write a function to make prediction
    def make_prediction(pipeline,encoder):
        gender = st.session_state["gender"]
        senior_citizen = st.session_state["senior_citizen"]
        partner = st.session_state["partner"]
        tenure = st.session_state["tenure"]
        monthly_charges = st.session_state["monthly_charges"]
        total_charges = st.session_state["total_charges"]
        payment_method = st.session_state["payment_method"]
        contract = st.session_state["contract"]
        paperless_billing = st.session_state["paperless_billing"]
        dependents = st.session_state["dependents"]
        phone_service = st.session_state["phone_service"]
        multiple_lines = st.session_state["multiple_lines"]
        streaming_tv = st.session_state["streaming_tv"]
        streaming_movies = st.session_state["streaming_movies"]
        online_security = st.session_state["online_security"]
        online_backup = st.session_state["online_backup"]
        device_protection = st.session_state["device_protection"]
        tech_support = st.session_state["tech_support"]
        internet_service = st.session_state["internet_service"]
        
        # create rows for the dataframe
        data=[[gender,senior_citizen,partner,tenure,monthly_charges,total_charges,
            payment_method,contract,paperless_billing,dependents,
            phone_service,multiple_lines,streaming_tv,streaming_movies,
            online_security,online_backup,device_protection,tech_support,
            internet_service]]
        # create columns for the dataframe
        columns = ['Gender','SeniorCitizen','Partner','Tenure','MonthlyCharges', 'TotalCharges'
                ,'PaymentMethod', 'Contract','PaperlessBilling','Dependents','PhoneService', 
                'MultipleLines','StreamingTV','StreamingMovies','OnlineSecurity', 
                'OnlineBackup', 'DeviceProtection', 'TechSupport','InternetService']
        df = pd.DataFrame(data=data,columns=columns)

        # make predictions
        pred = pipeline.predict(df)
        pred_int = int(pred[0])

        # transform the predicted variable 
        prediction = encoder.inverse_transform([[pred_int]])[0]

        # calculate prediction probability
        probability = pipeline.predict_proba(df)[0][pred_int]

        # Map probability to Yes or No
        prediction_label = "Yes" if pred_int == 1 else "No"

        # update the session state with the prediction and probability
        st.session_state["prediction"] = prediction
        st.session_state["prediction_label"] = prediction_label
        st.session_state["probability"] = probability
        
        # update the dataframe to capture predictions for the history page
        df["PredictionTime"] = datetime.date.today()
        df["ModelUsed"] = st.session_state["selected_model"]
        df["Prediction"] = st.session_state["prediction"]
        df["PredictionProbability"] = st.session_state["probability"]
        # export df as prediction_history.csv
        df.to_csv('./data/prediction_history.csv',mode="a", header=not os.path.exists('./data/prediction_history.csv'),index=False)
        return prediction,prediction_label,probability

    # create an initial instance of session state to hold prediction
    if "prediction" not in st.session_state:
        st.session_state.prediction = None

    if "probability" not in st.session_state:
        st.session_state.probability = None


    # write a function to show the forms to accepts input
    def display_forms():
        # call the get_selected_model function
        pipeline,encoder = get_selected_model(st.session_state.selected_model)

        with st.form('input-features'):
            col1,col2 = st.columns(2)
            with col1:
                st.write("## Personal Information 🧑‍💼")
                st.selectbox("Select your gender",options=["Male","Female"],key="gender")
                st.selectbox("Are you a senior citizen?",options=["Yes","No"],key="senior_citizen")
                st.selectbox("Do you have a dependent ?",options=["Yes","No"],key="dependents")
                st.selectbox("Do you have a partner?",options= ["Yes", "No",],key="partner")
                st.number_input("Enter your tenure",min_value = 0, max_value = 72,step=1, key="tenure")
                st.number_input("Enter your monthly charges",min_value=0.00, max_value = 200.00,step=0.10, key="monthly_charges")
                st.number_input("Enter you total charges per year",min_value=0.00,max_value=100000.00, step=0.10,key="total_charges")
                st.selectbox("Select your prefered contract type",options=["Month-to-month","One year","Two year"],key="contract")
                st.selectbox("Select your payment method",options= ["Electronic check", "Mailed check","Bank transfer (automatic)",
            "Credit card (automatic)"], key="payment_method")
            with col2:
                st.write("### Service Information 🛠️")
                st.selectbox("Do you have a phone service?",options=["Yes","No"],key="phone_service")
                st.selectbox("Do you have a multiple lines?",options=["Yes","No"],key="multiple_lines")
                st.selectbox("Which internet service do you prefer ?",options= ["Fiber optic", "No", "DSL"],key="internet_service")
                st.selectbox("Have you subscribed to our online security service?",options=["Yes","No"],key="online_security")
                st.selectbox("Have you subscribed to our online backup service?",options=["Yes","No"],key="online_backup")
                st.selectbox("Have you subscribed to our device protection service?",options=["Yes","No"],key="device_protection")
                st.selectbox("Have you subscribed to our tech support service?",options=["Yes","No"],key="tech_support")
                st.selectbox("Have you subscribed to our streaming TV service?",options=["Yes","No"],key="streaming_tv")
                st.selectbox("Have you subscribed to our streaming movies service?",options=["Yes","No"],key="streaming_movies")
                st.selectbox("Have you subscribed to our Paperless Billing Service?",options=["Yes","No"],key="paperless_billing")
            st.form_submit_button("Make Prediction",on_click=make_prediction,kwargs=dict(pipeline=pipeline,encoder=encoder))



        

    if __name__ == "__main__":
        
        # call the display_forms function
        display_forms()

        final_prediction = st.session_state["prediction"]
        if not final_prediction:
            st.write("## Prediction shows here")
            st.divider()
        else:
            # display the prediction result result
            col1,col2 = st.columns(2)
            with col1:
                st.write("### 👇Prediction Results")
                st.write(st.session_state["prediction"])
            with col2:
                st.write("### 🎯Prediction Probability")
                probability = st.session_state['probability']*100
                st.write(f"{probability:.2f}%")
                