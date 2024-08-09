import numpy as np
import pandas as pd
import streamlit as st
import pickle


team_names = ['Kolkata Knight Riders', 
         'Chennai Super Kings',
         'Kings XI Punjab', 
         'Rajasthan Royals',
         'Mumbai Indians',
         'Delhi Capitals',
         'Royal Challengers Bangalore',
         'Sunrisers Hyderabad',
         'Lucknow Super Giants',
         'Gujarat Titans'
         ]
cities = ['Centurion', 'Chandigarh', 'Delhi', 'Cuttack',
       'Mumbai', 'Ahmedabad', 'Sharjah', 'Dubai', 'Navi Mumbai',
       'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Cape Town',
       'Abu Dhabi', 'Rajkot', 'Durban', 'Jaipur', 'Pune', 'Lucknow',
       'Port Elizabeth', 'Indore', 'Dharamsala', 'Visakhapatnam',
       'Guwahati', 'Johannesburg', 'Raipur', 'Kanpur', 'Nagpur',
       'East London', 'Mohali', 'Kimberley', 'Bloemfontein', 'Ranchi']


# Streamlit App
st.title("IPL Match Outcome Predictor")
st.logo('./img/IPL_logo.png')

st.sidebar.header("Match Prediction Inputs")

def user_input_features():
    batting_team = st.sidebar.selectbox('Batting Team', sorted(team_names))
    available_bowling_teams = sorted([team for team in team_names if team != batting_team])
    bowling_team = st.sidebar.selectbox('Bowling Team', available_bowling_teams)
    city = st.sidebar.selectbox('City', sorted(cities))
    target = st.sidebar.number_input('Target', min_value=50, max_value=300, value=176)
    current_score = st.sidebar.number_input('Current Score', min_value=0, max_value=300, value=100)
    over = st.sidebar.slider('Overs', int(20), int(0), int(20))
    wickets = st.sidebar.slider('Wickets', int(0), int(10), int(0))
   
    data = {
        'batting_team': batting_team,
        'bowling_team': bowling_team,
        'city': city,
        'target': target,
        'current_sore': current_score,
        'over': over,
        'wickets': wickets,
    }
    features = pd.DataFrame(data, index=[0])
    return features

input_data = user_input_features()

# Display the input data
st.subheader('Match Input Details')
st.write(input_data)

# Create DataFrame from Input
input_df = pd.DataFrame({'batting_team':input_data['batting_team']
                           ,'bowling_team':input_data['bowling_team']
                           ,'city':input_data['city']
                           ,'chase_target':input_data['target']
                           ,'current_sore':input_data['current_sore']
                           ,'run_rate': np.where(input_data['over']>0,
                                        (input_data['current_sore']/input_data['over'])/6,
                                        input_data['current_sore'])
                           ,'ball_left':120-(input_data['over']*6)
                           ,'wickets_left':10-input_data['wickets']
                           ,'runs_left':input_data['target']-input_data['current_sore']
    }
)
# Load Model file
pipe = pickle.load(open('.\model\model.pkl', 'rb'))

# Prediction
if st.button('Predict'):
    result = pipe.predict_proba(input_df)
    win_probability = round(result[0][1] * 100)
    loss_probability = round(result[0][0] * 100)
    result_text = 'Win'   
    st.subheader('Prediction')
    bolwing=''
    batting=''
    result_w=''
    result_l=''
    if win_probability>loss_probability:
        bolwing= input_data['bowling_team'].iloc[0]
        batting= input_data['batting_team'].iloc[0]
        result_w=win_probability
        result_l=loss_probability
    else:
        bolwing= input_data['batting_team'].iloc[0]
        batting= input_data['bowling_team'].iloc[0]
        result_w=loss_probability
        result_l=win_probability
    st.markdown(f"""
                <b style="color: #FF5733;">{bolwing}</b>  holds a strong {result_w}% chance of victory,<br>
                while <b style="color: #1E90FF;">{batting}</b> faces an uphill battle with just a {result_l}% chance of winning!
                """, unsafe_allow_html=True)

