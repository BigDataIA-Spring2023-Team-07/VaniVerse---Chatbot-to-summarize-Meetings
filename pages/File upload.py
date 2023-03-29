import streamlit as st
import boto3
import os
from dotenv import load_dotenv
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from backend import common_utils, chatgpt

load_dotenv()


st.title("Model as a Service - Meeting Summary :page_with_curl:")

st.header("Please upload the audio file :mega:")

audio_file = st.file_uploader("Upload audio file (Limit 25Mb)", type=['mp4', 'mp3', 'wav'])

language = st.selectbox('Audio Language:', ['English', 'Otherss'])

if st.button("Submit"):
    if audio_file is None:
        st.error("Please upload the audio file")
    
    # check if the file is mp4
    elif (audio_file.name[-4:] != ".mp4") and (audio_file.name[-4:] != ".mp3") and (audio_file.name[-4:] != ".wav"):
            st.error("Please upload the audio file in mp4 format")  
    else:
        st.write("File name: ", audio_file.name)
        st.write("File size: ", audio_file.size/1048576 , "MB")
        st.write("Audio Language: ", language)
        if audio_file.size/1048576 > 25:
            st.error("File size should be less than 25MB")
        s3client = boto3.client('s3', region_name= "us-east-1", aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'), aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'))
        with st.spinner("Uploading file to S3"):
            # s3client.put_object(Bucket='damg7245-team7', Key= 'Adhoc/' + audio_file.name , Body=audio_file.read())
            audio_file_name= audio_file.name[:-4] + '_' + language + audio_file.name[-4:]
            common_utils.uploadfile(audio_file_name, audio_file.read())
            st.success("File uploaded to S3 successfully")

            # triggering the DAG
            response = common_utils.trigger_dag(audio_file_name)
            if response.status_code == 200:
                st.success('DAG triggered successfully')
            else:
                st.error(f'Error triggering DAG: {response.text}')




# Fetch files from S3 and store the filenames in a list
st.header("Select a file from the list :three_button_mouse:")

file_list = chatgpt.getfilenames()

# Display the list of files in a dropdown
file_selected = st.selectbox("Select a file", np.unique(file_list))
st.write("You selected: ", file_selected)




# Select the qn from dropdown list
message_history = []
st.header("Select a question from the list :grey_question:")
qn_selected = st.selectbox("Select a question", ["Can you summarize ?", "What is the main topic?", "How was the tone?", "Any things which needs to be done later?", "Custom"])

if qn_selected == "Custom":
    qn_selected = st.text_input("Enter your question")

st.write("Your Question: ", qn_selected)
message_history.append({"role": "user", "content": f"{qn_selected}"})

if st.button("Process"):
     with st.spinner("Processing your request"):
        reply = chatgpt.getdefaultquestion(qn_selected, file_selected, message_history)
        if len(reply) == 0:
            st.write("No response from the model. Please try again")
        else:
            st.write("Answer:", reply)

