import streamlit as st
import pandas as pd
import sqlite3


df_hosp= pd.read_csv('Patient_survey__HCAHPS__-__Hospital.csv', encoding = "utf-8")
hosp_surveys = df_hosp.to_dict("records")

conn= sqlite3.connect('HospSurveys.db')
cursor = conn.cursor()

#returns list of hospitals and associated data
def scoped_hospitals(hosp_surveys):
    hospital_attr=['Facility ID','Facility Name','Address','City','State','ZIP Code','County Name','Phone Number']
    hospital_data_list=[]
    for hosp_survey in hosp_surveys:
        hospital_data_list.append({k:v for k,v in hosp_survey.items() if k in hospital_attr})
    return hospital_data_list

#change scoped_hospitals list to a df
pd_hospitals = pd.DataFrame.from_dict(scoped_hospitals(hosp_surveys))

#returns list of hospitals facility id and survey questions
def scoped_survey_questions(hosp_surveys):
    survey_questions=['Facility ID','HCAHPS Answer Description', 'HCAHPS Answer Percent', 'Number of Completed Surveys', 'Survey Response Rate Percent']
    clean = ['Room was "always" clean']
    questions_list=[]
    for hosp_survey in hosp_surveys:
        questions_list.append({k:v for k,v in hosp_survey.items() if k in survey_questions})
    return questions_list

#change scoped_surveys list to a df
scoped_surveys= scoped_survey_questions(hosp_surveys)
pd_surveys = pd.DataFrame.from_dict(scoped_surveys)

# get all scoped string coordinates, clean data and add 0,0 for lat, long if equal to string =keep, 
# else add (0,0) to replace the NaN. 
def hosp_coordinates(hosp_surveys):
    str_coordinates=[]
    for hospital in hosp_surveys:
        if type(hospital['Location'])== str:
            str_coordinates.append([float(coord) for coord in hospital['Location'][7:-1].split()])
        else:
            str_coordinates.append([0, 0])
    return str_coordinates

coor = hosp_coordinates(hosp_surveys)

# use panda dataframe add lat/long values in Location column with list of values from coor to pd_hospitals df
pd_hospitals['Location'] = coor
pd_hospitals

# change values in location column to string type otherwise it generates an error type
# when convert table to sql for int,floats and strings
pd_hospitals['Location']=pd_hospitals['Location'].astype(str)

# change values in facility id column to string
pd_hospitals['Facility ID']=pd_hospitals['Facility ID'].astype(str)

#survey df to sql table
pd_surveys.to_sql('surveys_table', conn, index = False, if_exists='replace')

#hospital df to sql table
pd_hospitals.to_sql('hospitals_table', conn, index = False, if_exists='replace')

#define a function that returns a list of hospital names
def hospital_names():
    hospitals= pd.read_sql('SELECT DISTINCT "Facility Name" from hospitals_table ORDER BY "Facility Name"', conn).to_dict('records')
    hospitals_data = [hospital['Facility Name'] for hospital in hospitals]
    return hospitals_data

hospital_list = hospital_names()

#define a function that returns a list of survey answer 'Room was "always" clean'
def clean_surveys():
    surveys= pd.read_sql('''SELECT DISTINCT "Facility ID", "HCAHPS Answer Description", "HCAHPS Answer Percent"
    from surveys_table WHERE "HCAHPS Answer Description" = 'Room was "always" clean'
    AND "HCAHPS Answer Percent" != 'Not Available' ORDER BY "HCAHPS Answer Percent" DESC''', conn).to_dict('records')
    return surveys

surveys_list = clean_surveys()



st.title('Patient Hospital Ratings')

st.slider('Hospital room cleanliness rating', 0, 100)

st.multiselect('Choose a hospital', hospital_list)

