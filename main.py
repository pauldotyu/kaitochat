import json
import os
import streamlit as st
from kaito import Kaito

SYSTEM_MESSAGE = {"role": "assistant", "content": "How can I help you today?"}
if "messages" not in st.session_state:
    st.session_state['messages'] = [SYSTEM_MESSAGE]

# Function to clear chat history
def clear_chat_history():
    st.session_state['messages'] = [SYSTEM_MESSAGE]

# Main title
st.title('🦜🔗 KAITO Chat')

with st.sidebar:
  st.title('Settings')
  
  model_endpoint = st.text_input('Endpoint', value=os.getenv('MODEL_ENDPOINT', ''), help='The endpoint of the model to use for the chatbot.')
  model_name = st.text_input('Model name', value=os.getenv('MODEL_NAME'), help='Enter the name of the model to use for the chatbot.')
  response_temperature = st.sidebar.slider('Temperature', min_value=0.01, max_value=1.0, value=0.7, step=0.01, help='The temperature to use when generating text. The higher the temperature, the more creative the response.')
  response_top_k = st.sidebar.slider('Top K', min_value=0, max_value=1, value=-1, step=1, help='The number of top tokens to consider. Set to -1 to consider all tokens.')
  response_top_p = st.sidebar.slider('Top P', min_value=0.01, max_value=1.0, value=0.9, step=0.01, help='The cumulative probability threshold for nucleus sampling.')
  response_repetition_penalty = st.sidebar.slider('Repetition Penalty', min_value=0.0, max_value=2.0, value=1.0, step=0.01, help='The repetition penalty to use when generating text.')
  response_max_tokens = st.sidebar.slider('Max Tokens', min_value=200, max_value=2000, value=2000, step=100, help='The maximum number of tokens to generate in the response.')

  # Button to start a new chat
  st.button('New chat', on_click=clear_chat_history)

if model_endpoint:
  model = Kaito(endpoint=model_endpoint,model_name=model_name,max_tokens=response_max_tokens,temperature=response_temperature,top_k=response_top_k,top_p=response_top_p,repetition_penalty=response_repetition_penalty)

  # Display chat messages from history on app rerun
  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  # Set a default model deployment
  if "model_endpoint" not in st.session_state:
    st.session_state["model_endpoint"] = model_endpoint
  
  # Accept user input
  if prompt := st.chat_input("Type a message..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
      st.markdown(prompt)

    # Invoke the call to KAITO's inferencing endpoint
    try:
      # Get session_state.messages from 1 index to the last index minus 1
      messages = st.session_state.messages[1:-1]
      
      # Get the user's prompt
      prompt = st.session_state.messages[-1]["content"]

      # Build a chat history string from the messages
      chat_history = [{"role": message['role'], "content": message['content']} for message in messages]
      chat_history.append({"role": "user", "content": prompt})
      # Invoke the model with the user's prompt and chat history
      response_stream = model._call(json.dumps(chat_history))

      # Create a placeholder to display the model's response 
      response_placeholder = st.empty()
      full_response = ""
      
      # Display the response in the chat message container    
      with st.chat_message("assistant"):
        for chunk in response_stream:
          full_response += chunk
          response_placeholder.markdown(full_response + " ")
        response_placeholder.markdown(full_response)
      
      # Add the model's response to the chat history
      st.session_state.messages.append({"role": "assistant", "content": full_response})
    except Exception as e:
      st.error(e)
else:
  st.warning('Please enter the model inference endpoint to use for the chatbot.')