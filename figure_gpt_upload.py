from distutils.command import upload
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import openai
import os

## Setting up open ai
openai.api_key = st.secrets['openai_api_key']


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


## Prepping the Model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

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
                for response in openai.ChatCompletion.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {'role':'system', 'content': 'You are a helpful assistant.'},
                        {'role':'system', 'content': 'I have provided you a dataset with a head that looks like '+df.head().to_string()},
                        {'role':'user', 'content': prompt}
                    ],
                    stream=True,
                ):
                    full_response += response.choices[0].delta.get("content", "")
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            #st.session_state.messages.append({"role": "assistant", "content": full_response}) 


if st.session_state['plot_boolean'] == True: 
    if prompt := st.chat_input("What kind of plot do you want?"):
            #st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                for response in openai.ChatCompletion.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {'role':'system', 'content': 'Only return python code.'},
                        {'role':'system', 'content': 'I have provided you a dataset with a head that looks like '+df.head().to_string()},
                        {'role':'user', 'content': prompt}
                    ],
                    stream=True,
                ):
                    full_response += response.choices[0].delta.get("content", "")
                    #message_placeholder.markdown(full_response + "▌")
                #message_placeholder.markdown(full_response)
                exec(full_response)
            #st.session_state.messages.append({"role": "assistant", "content": full_response}) 
