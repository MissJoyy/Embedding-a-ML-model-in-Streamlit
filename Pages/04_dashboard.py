import streamlit as st
import plotly.express as px
import pandas as pd
import altair as alt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Page configurations
st.set_page_config(
    page_title ='Dashboard Page',
    page_icon ='📈',
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
    username: apaloojoy
    password: 1234
    '''
    st.code(test_code)
        
elif st.session_state["authentication_status"] == False:
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
    

    #### Add contents to the Sidebar
    with st.sidebar:
        # Filter the data based on the gender,contract_type,payment_method and analysis
        st.title("Select Filters")
        st.selectbox("Gender",options=["Male","Female"],key="gender")
        st.selectbox("Contract",options=["Month-to-month","One year","Two year"],key="contract")
        st.selectbox("Payment Method",options=["Electronic check","Mailed check","Bank transfer (automatic)","Credit card (automatic)"],key="payment_method")
        st.selectbox("Type of Analysis",options=["Univariate","Bivariate","Multivariate"],key="analysis")

    st.markdown("<style>div.block-container{padding-top:1rem;}</style>",unsafe_allow_html=True)

    # set page theme
    alt.themes.enable("dark")

    # set custom color_map
    color_map = {"Yes":"green","No":"pink"}

    # read data for dashboard
    df = pd.read_csv("./data/telco_churn_full_training.csv")

    # Filter data based on categories
    if st.session_state.gender:
        gender_filter = df[df["Gender"]==st.session_state.gender]

    if st.session_state.contract:
        contract_filter = gender_filter[gender_filter["Contract"]==st.session_state.contract]

    if st.session_state.payment_method:
        payment_method_filter = contract_filter[contract_filter["PaymentMethod"]==st.session_state.payment_method]



    df = payment_method_filter



    # Create a function to view the EDA
    def eda_dashboard():
        st.markdown("### Exploratory Data Analysis ")
        st.write("#")
        if st.session_state.analysis == "Univariate":
            st.markdown("#### Univariate Analysis")
            col1,col2 = st.columns(2)
            with col1:
                monthlycharges_histogram = px.histogram(df,x="MonthlyCharges",title="Distribution of MonthlyCharges")
                st.plotly_chart(monthlycharges_histogram)
            with col2:
                totalcharges_histgram = px.histogram(df,x="TotalCharges",title="Distribution of TotalCharges")
                st.plotly_chart(totalcharges_histgram)

            col3,col4 = st.columns(2)
            with col3:
                # plot a histogram of Tenure
                tenure_histogram = px.histogram(df,x="Tenure",title="Distribution of Tenure")
                st.plotly_chart(tenure_histogram)
            with col4:
                pieplot = px.pie(df,names="Churn",title="Churn by InternetService",color="Churn",color_discrete_map=color_map,hole=0.3)
                st.plotly_chart(pieplot)
                
            col5,col6 = st.columns(2)
            with col5:
                boxplot = px.box(df,x="TotalCharges",title="BoxPlot of TotalCharges")
                st.plotly_chart(boxplot)
            with col6:
                boxplot = px.box(df,x="Tenure",title="BoxPlot of Tenure")
                st.plotly_chart(boxplot)

            boxplot = px.box(df,x="MonthlyCharges",title="Boxplot of MonthlyCharges")
            st.plotly_chart(boxplot)


        elif st.session_state.analysis == "Bivariate":
            st.write("#")
            st.markdown("#### Bivariate Analysis")
            col1,col2 = st.columns(2)
            with col1:
                boxplot = px.box(df,x="MonthlyCharges",y="Churn",color="Churn",color_discrete_map=color_map,title="Distribution of Churn by MonthlyCharges")
                st.plotly_chart(boxplot)
            with col2:
                boxplot = px.box(df,x="TotalCharges",y="Churn",color="Churn",color_discrete_map=color_map,title="Distribution of Churn by TotalCharges")
                st.plotly_chart(boxplot)

            col3,col4 = st.columns(2)
            with col3:
                boxplot = px.box(df,x="Tenure",y="Churn",color="Churn",color_discrete_map=color_map,title="Distribution of Churn by Tenure")
                st.plotly_chart(boxplot)
            with col4:
                barplot = px.bar(df,x="InternetService",y="MonthlyCharges",color="Churn",color_discrete_map=color_map)
                st.plotly_chart(barplot)
            
            col5,col6 = st.columns(2)
            with col5:
                    numerical_data = df.select_dtypes("number")
                    numerical_data.drop(columns=["Unnamed: 0"],inplace=True)
                    cor_matrix = numerical_data.corr()
                    heat_map = px.imshow(cor_matrix,text_auto=True,aspect="auto",title="Correlation Matrix")
                    st.plotly_chart(heat_map)
            with col6:
                churn_count_df = df.groupby(["PaymentMethod","Churn"]).size().reset_index(name="count").sort_values(by="count",ascending=False)
                barplot = px.bar(churn_count_df,x="PaymentMethod",y="count",color="Churn",color_discrete_map=color_map,title="Count of Churn By Payment Method")
                st.plotly_chart(barplot)

                    
        else:
            st.write("#")
            st.markdown("#### Multivariate Analysis")
            col1,col2 = st.columns(2)
            with col1:
                scatter_plot = px.scatter(df,x="MonthlyCharges",y="TotalCharges",color="Churn",color_discrete_map=color_map,title="Relation Between Churn and Charges")
                st.plotly_chart(scatter_plot)
            with col2:
                # PERFORM pca ANALYSIS
                numeric_features = df.select_dtypes(include=["float64","int64"])
                numeric_features = numeric_features.dropna()
                if not numeric_features.empty:
                    standardized_features = StandardScaler().fit_transform(numeric_features)
                    pca_full = PCA().fit(standardized_features)
                    explained_variance = pca_full.explained_variance_ratio_


                scree_plot = px.line(
                x=range(1, len(explained_variance) + 1),
                y=explained_variance,
                markers=True,
                title="Principal Component Analysis",
                labels={"x": "Principal Component", "y": "Explained Variance Ratio"} )
                st.plotly_chart(scree_plot)
            
            
        
            
    def kpi_dashboard():
        st.markdown(" ### Key Performance Index")
        col1,col2,col3 = st.columns(3)
        with col1: 
            st.markdown(
                f"""
                <div style="background-color: lightgreen; border-radius:10px; width:80%; margin-top: 20px>
                    <h3 style="margin-left:30px">Quick Stats About Dataset</h3>
                    <hr>
                    <h5 style="margin-left:30px">Churn Rate: {(df["Churn"].value_counts(normalize=True).get("Yes",0)*100):.2f}%</h5>
                    <hr>
                    <h5 style="margin-left:30px"> Average Monthly Charges: $ {df["MonthlyCharges"].mean():.2f}</h5>
                    <hr>
                    <h5 style="margin-left:30px"> Average Yearly Charges: $ {df["TotalCharges"].mean():.2f}</h5>
                    <hr>
                    <h5 style="margin-left:30px">Number of Customers: {df.size}</h5>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col2:
            violin_plot = px.violin(df,x="Churn",y="MonthlyCharges",title="Impact of Monthly Charges On Customer Churn",color="Churn",color_discrete_map=color_map)
            st.plotly_chart(violin_plot)
        with col3:
            churn_by_mu_multipleLiservice = px.bar(df,x="MultipleLines",y="MonthlyCharges",color="Churn",color_discrete_map=color_map,title="Churn by Multiple Services and Monthly Charges")
            st.plotly_chart(churn_by_mu_multipleLiservice)

        col4,col5,col6 = st.columns(3)
        with col4:
            churn_by_contract= px.bar(df,x="Contract",y="MonthlyCharges",color="Churn",color_discrete_map=color_map,title="Churn by Contract Type and Monthly Charges")
            st.plotly_chart(churn_by_contract)
        with col5:
            churn_by_streaming_tv = px.bar(df,x="StreamingTV",y="MonthlyCharges",color="Churn",color_discrete_map=color_map,title="Churn by Streaming TV and Monthly Charges")
            st.plotly_chart(churn_by_streaming_tv)
        with col6:
            churn_by_techsupport = px.bar(df,x="TechSupport",y="MonthlyCharges",color="Churn",color_discrete_map=color_map,title="Churn by Tech Support and Monthly Charges")
            st.plotly_chart(churn_by_techsupport)

        col7,col8,col9 = st.columns(3)
        with col7:
            monthly_charges_and_tenure = px.scatter(df,x="Tenure",y="MonthlyCharges",color="Churn",color_discrete_map=color_map,title="Relationship Between Monthly Charges and Tenure")
            st.plotly_chart(monthly_charges_and_tenure)
        with col8:
            total_charges_and_tenure = px.scatter(df,x="Tenure",y="TotalCharges",color="Churn",color_discrete_map=color_map,title="Relationship Between Total Charges and Tenure")
            st.plotly_chart(total_charges_and_tenure)
        with col9:
            tenure_versus_charges = px.density_contour(df,x="Tenure",color="Churn",color_discrete_map=color_map,marginal_x="histogram",marginal_y="histogram",title="Tenure by Churn Status")
            st.plotly_chart(tenure_versus_charges)

    if __name__ == "__main__":
        # set page title
        st.title("Dashboard Page ")

        col1,col2 = st.columns(2)
        with col1:
            pass
        with col2:
            st.selectbox("Select Dashboard Type",options=["EDA","KPI"],key="selected_dashboard_type")

        if st.session_state.selected_dashboard_type == "EDA":
            eda_dashboard()
        else:
            kpi_dashboard()