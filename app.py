import json
import os
import streamlit as st
from groq import Groq  # 1. Swapped from OpenAI to Groq

st.title("🤖 Free Llama 3 Bot via Groq")

HISTORY_FILE = "chat_history.json"

# 2. Initialize the Groq client (automatically looks for GROQ_API_KEY)
client = Groq()

def load_chat_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return [{"role": "system", "content": "You are a helpful AI assistant."}]

def save_chat_history(messages):
    with open(HISTORY_FILE, "w") as f:
        json.dump(messages, f, indent=4)

if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

if user_input := st.chat_input("Type your message here..."):
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    save_chat_history(st.session_state.messages)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        # 3. Call Groq's chat completion with a supported model
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=st.session_state.messages
        )
        
        ai_response = completion.choices[0].message.content
        response_placeholder.write(ai_response)
        
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    save_chat_history(st.session_state.messages)
