from distutils.command import upload
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from openai import AzureOpenAI

## Setting up the Openai client
client = AzureOpenAI(
  api_key = st.secrets['openai_api_key'],  
  api_version = "2023-03-15-preview",
  azure_endpoint = "https://stratus-embeddings-south-central.openai.azure.com/"
)

## Uploading a file
st.title('FigureGPT')
st.write('Please upload a csv or xlsx file for chatgpt to analyze. Please note, this file will stay local and will not be uploaded to chatgpt.')
uploaded_file = st.file_uploader("Choose a file for chatgpt to analyze.")
if uploaded_file is not None: 
    if 'csv' in uploaded_file.name:
        df = pd.read_csv(uploaded_file)
    elif 'xlsx' in uploaded_file.name:
        df = pd.read_excel(uploaded_file)

    st.write('Here is the data:')
    st.write(df.head())

    # If one button is pressed call the information chatbot. 
    # If another button is pressed call the plotting chatbot. 

    # Prepping the Model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-35-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "plot_boolean" not in st.session_state:
    st.session_state['plot_boolean'] = False

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

description_button = st.button(
    label = 'Press me to chat about the data.',
    key = 'description_button'
)

plot_button = st.button(
    label = 'Press me to plot the data.',
    key = 'plot_button'
)

if plot_button:
    st.session_state['plot_boolean'] = True

if description_button: 
    st.session_state['plot_boolean'] = False

if st.session_state['plot_boolean'] == False: 
    if prompt := st.chat_input("What do you want to know about the data?"):
            #st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

                response = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {'role':'system', 'content': 'You are a helpful assistant.'},
                        {'role':'system', 'content': 'I have provided you a dataset with a head that looks like '+df.head().to_string()},
                        {'role':'user', 'content': prompt}
                    ],
                )
                message_placeholder.markdown(response.choices[0].message.content)
            #st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content}) 


if st.session_state['plot_boolean'] == True: 
    if prompt := st.chat_input("What kind of plot do you want?"):
            #st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                #for response in openai.ChatCompletion.create(
                response = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {'role':'system', 'content': 'Only return python code.'},
                        {'role':'system', 'content': 'I have provided you a dataset with a head that looks like '+df.head().to_string()},
                        {'role':'user', 'content': 'Return just the python code to' + prompt+' In the dataframe df. Use plotly and streamlit.'}
                    ]
                )
                #):
                full_response = response.choices[0].message.content
                    #full_response += response.choices[0].delta.get("content", "")
                    #message_placeholder.markdown(full_response + "▌")
                #message_placeholder.markdown(full_response)
                message_placeholder.markdown(full_response)
                try:
                    exec(full_response)
                except: 
                    full_response = full_response[full_response.find('python')+6:]
                    full_response = full_response[:full_response.find('```')]
                    try:
                        exec(full_response)
                    except:
                        print(full_response)