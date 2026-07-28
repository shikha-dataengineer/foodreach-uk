#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import joblib
import pandas as pd

# Load the trained model and encoder
rf_model = joblib.load('rf_model.pkl')
encoder = joblib.load('encoder.pkl')

# Define the response options with emojis
response_options = {
    "Never 😌": 0,
    "Almost never 🙃": 1,
    "Sometimes 😐": 2,
    "Fairly often 😟": 3,
    "Very often 😫": 4
}

def main():
    st.title("University Student Survey")

    # Initial Form to check stress frequency
    with st.form(key='initial_form'):
        student_name = st.text_input("Student Name:")
        stress_frequency = st.selectbox(
            "How often have you felt stressed over the last three months?", 
            options=list(response_options.keys()), 
            index=2
        )
        initial_submit_button = st.form_submit_button(label='Next')

    if initial_submit_button:
        if stress_frequency in ["Never 😌", "Almost never 🙃"]:
            st.success("Thank you for participating in the survey! 😊")
            st.write("We appreciate your time and are glad to hear that you haven't been feeling stressed. Stay healthy and happy!")
        else:
            # Main Form for detailed survey
            with st.form(key='survey_form'):
                gender = st.selectbox("Gender", options=["Male 🧑‍💼", "Female 👩‍💼", "Other 🧑‍⚕️"], index=1)
                ethnicity = st.selectbox("Ethnicity", options=["White 🏳️", "Black 🏴", "Asian 🏮", "Other 🌍"], index=0)
                age = st.number_input("Please state your age in years:", min_value=18, max_value=100, value=27, step=1)
                university_location = st.text_input("University location:")
                tuition_fee_status = st.selectbox("What is your tuition fee status?", options=["Domestic 🏠", "International 🌏", "EU 🇪🇺"], index=1)
                postgraduate_qualification = st.selectbox("What postgraduate qualification are you studying for?", options=["Masters 🎓", "PhD 🎓", "Other 📚"], index=1)
                year_of_study = st.selectbox("What is your year of study?", options=["1 🥇", "2 🥈", "3 🥉", "4 and above 🏆"], index=0)
                subject_of_study = st.selectbox("What is your subject of study?", options=["Arts and Humanities 🎨", "Sciences 🔬", "Engineering 🛠", "Other 📖"], index=0)
                
                # Collecting symptom data
                st.header("Symptom-related Questions:")
                low_energy = st.selectbox("Low energy", options=list(response_options.keys()), index=2)
                headaches = st.selectbox("Headaches", options=list(response_options.keys()), index=1)
                digestion_problems = st.selectbox("Digestion problems", options=list(response_options.keys()), index=0)
                anxiety_or_tension = st.selectbox("Anxiety or tension", options=list(response_options.keys()), index=3)
                sleep_problems = st.selectbox("Sleep problems", options=list(response_options.keys()), index=4)
                rapid_heartbeat = st.selectbox("Rapid heartbeat or palpitations", options=list(response_options.keys()), index=4)
                irritability = st.selectbox("Irritability", options=list(response_options.keys()), index=2)
                concentration_problems = st.selectbox("Concentration problems", options=list(response_options.keys()), index=2)
                sadness_or_tears = st.selectbox("Sadness or tearfulness", options=list(response_options.keys()), index=2)
                illness = st.selectbox("Illness", options=list(response_options.keys()), index=4)
                aches_and_pains = st.selectbox("Aches and pains not due to injury", options=list(response_options.keys()), index=2)
                loneliness = st.selectbox("Loneliness", options=list(response_options.keys()), index=2)
                
                st.header("Support and Coping Mechanisms:")
                coping_mechanisms = st.text_area("Please describe your coping mechanisms for stress:")
                coping_success = st.selectbox("Do you feel that your coping mechanisms help to manage or relieve stress successfully?", options=["Yes", "No"], index=0)
                university_support = st.selectbox("Do you feel that you are getting enough support from your university?", options=["Yes", "No"], index=0)
                
                st.header("Additional Factors:")
                feeling_overloaded = st.selectbox("Feeling overloaded with university work", options=list(response_options.keys()), index=2)
                time_spent_onsite = st.selectbox("Spending too much time onsite at university", options=list(response_options.keys()), index=2)
                peer_competition = st.selectbox("Competition with peers", options=list(response_options.keys()), index=2)
                difficulties_with_supervisor = st.selectbox("Difficulties with supervisor or tutor", options=list(response_options.keys()), index=2)
                unpleasant_working_environment = st.selectbox("Unpleasant working environment", options=list(response_options.keys()), index=2)
                criticism_about_work = st.selectbox("Criticism about work", options=list(response_options.keys()), index=2)
                lack_of_time_for_relaxation = st.selectbox("Lack of time for relaxation", options=list(response_options.keys()), index=2)
                difficult_home_environment = st.selectbox("Difficult home environment", options=list(response_options.keys()), index=2)
                financial_issues = st.selectbox("Financial issues", options=list(response_options.keys()), index=2)
                lack_of_confidence_with_academic_performance = st.selectbox("Lack of confidence with academic performance", options=list(response_options.keys()), index=2)
                lack_of_confidence_with_subject_or_career_choice = st.selectbox("Lack of confidence with subject or career choice", options=list(response_options.keys()), index=2)
                conflicts_between_university_and_employment = st.selectbox("Conflicts between university work and extracurricular employment", options=list(response_options.keys()), index=2)
                
                additional_factors = st.text_area("Please describe anything else that has influenced your stress/anxiety levels over the last three months:")
                
                submit_button = st.form_submit_button(label='Submit')

                if submit_button:
                    # Create input data
                    input_data = [
                        gender, ethnicity, age, university_location, tuition_fee_status, postgraduate_qualification,
                        year_of_study, subject_of_study, stress_frequency, low_energy, headaches, digestion_problems,
                        anxiety_or_tension, sleep_problems, rapid_heartbeat, irritability, concentration_problems,
                        sadness_or_tears, illness, aches_and_pains, loneliness, coping_mechanisms,
                        coping_success, university_support, feeling_overloaded, time_spent_onsite, peer_competition,
                        difficulties_with_supervisor, unpleasant_working_environment, criticism_about_work,
                        lack_of_time_for_relaxation, difficult_home_environment, financial_issues,
                        lack_of_confidence_with_academic_performance, lack_of_confidence_with_subject_or_career_choice,
                        conflicts_between_university_and_employment
                    ]
                    features = [
                        'Gender', 'Ethnicity', 'Age', 'University_Location', 'Tuition_Fee_Status', 'Postgrad_Qualification',
                        'Year_of_Study', 'Subject_of_Study', 'Stress_Frequency', 'Low_Energy_Frequency', 'Headaches_Frequency',
                        'Digestion_Problems_Frequency', 'Anxiety_or_Tension_Frequency', 'Sleep_Problems_Frequency',
                        'Rapid_Heartbeat_or_Palpitations_Frequency', 'Irritability_Frequency', 'Concentration_Problems_Frequency',
                        'Sadness_or_Tearfulness_Frequency', 'Illness_Frequency', 'Aches_and_Pains_Frequency', 'Loneliness_Frequency',
                        'Coping_Success', 'University_Support', 'Feeling_Overloaded', 'Time_Spent_Onsite',
                        'Peer_Competition', 'Difficulties_with_Supervisor', 'Unpleasant_Working_Environment', 'Criticism_About_Work',
                        'Lack_of_Time_for_Relaxation', 'Difficult_Home_Environment', 'Financial_Issues',
                        'Lack_of_Confidence_with_Academic_Performance', 'Lack_of_Confidence_with_Subject_or_Career_Choice',
                        'Conflicts_between_University_and_Employment', 'Additional_Factors'
                    ]

                    # Preprocess the input data
                    input_df = pd.DataFrame([input_data], columns=features)
                    input_encoded = encoder.transform(input_df.select_dtypes(include=['object', 'category']).astype(str))

                    # Predict stress level
                    prediction = rf_model.predict(input_encoded)

                    st.success("Thank you for submitting the survey! 😊")
                    st.write(f"Your predicted stress level is: {prediction[0]}")

if __name__ == "__main__":
    main()

