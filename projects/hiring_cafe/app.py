import streamlit as st
import pandas as pd
import numpy as np
import pickle

# Load the model and encoding information
# (You'll need to save these first - see code below)
with open('salary_model.pkl', 'rb') as f:
    salary_model = pickle.load(f)

with open('model_columns.pkl', 'rb') as f:
    model_columns = pickle.load(f)

with open('model_residual_std.pkl', 'rb') as f:
    log_residual_std = pickle.load(f)

# Streamlit app
st.title("Salary Predictor")
st.write("Enter your job parameters to get a salary prediction range")

# User inputs
workplace_type = st.selectbox(
    "Workplace Type",
    ["Hybrid", "Remote", "Onsite"]
)

workplace_state = st.selectbox(
    "Workplace State",
    ["california, us", "new york, us", "texas, us", "florida, us", "georgia, us"]
)

seniority_level = st.selectbox(
    "Seniority Level",
    ["No Prior Experience Required", "Entry Level", "Mid Level", "Senior Level"]
)

years_of_experience = st.number_input(
    "Years of Experience in Role",
    min_value=0, max_value=50, value=5
)

technical_tools = st.multiselect(
    "Technical Tools/Skills",
    ["python", "sql", "java", "javascript", "r", "c++", "aws", "azure", "docker", "kubernetes"]
)

# Prepare prediction data
if st.button("Predict Salary"):
    # Create a dataframe with the user inputs
    pred_data = pd.DataFrame([[0] * len(model_columns)], columns=model_columns)
    
    # Set the constant
    pred_data['const'] = 1
    
    # Set years of experience
    pred_data['job_data.min_industry_and_role_yoe'] = years_of_experience
    
    # Set categorical dummies
    pred_data[f'job_data.workplace_type_{workplace_type}'] = 1
    pred_data[f'job_data.workplace_states_{workplace_state}'] = 1
    pred_data[f'job_data.seniority_level_{seniority_level}'] = 1
    
    for tool in technical_tools:
        col_name = f'job_data.technical_tools_{tool}'
        if col_name in pred_data.columns:
            pred_data[col_name] = 1
    
    # Ensure columns match model
    pred_data = pred_data[model_columns]
    
    # Make prediction
    log_pred = salary_model.predict(pred_data)[0]
    salary_pred = np.exp(log_pred)
    

    # Calculate confidence interval on log scale

    log_lower = log_pred - (1.96 * log_residual_std)
    log_upper = log_pred + (1.96 * log_residual_std)

    # Transform back to salary scale
    lower_bound = np.exp(log_lower)
    upper_bound = np.exp(log_upper)
    
    st.success("Predicted Salary Range:")
    st.metric("Lower Bound", f"${lower_bound:,.0f}")
    st.metric("Predicted", f"${salary_pred:,.0f}")
    st.metric("Upper Bound", f"${upper_bound:,.0f}")
