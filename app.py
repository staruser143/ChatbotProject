import json
import os
import streamlit as st
from groq import Groq  # 1. Swapped from OpenAI to Groq

st.title("🤖 Free Model Bot via Groq")



# 2. Initialize the Groq client (automatically looks for GROQ_API_KEY)
client = Groq()

if "messages" not in st.session_state:
    st.session_state.messages = [ 
        {"role":"system","content":"You are a helpful, concise AI assiant."}
    ]
# 3. Display past message on screen refresh
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

if user_input := st.chat_input("Type your message here..."):
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        # 3. Call Groq's chat completion with a supported model
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=st.session_state.messages
        )
        
        ai_response = completion.choices[0].message.content
        response_placeholder.write(ai_response)
        
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

