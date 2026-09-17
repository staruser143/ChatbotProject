import json
import os
import streamlit as st
from groq import Groq  # 1. Swapped from OpenAI to Groq

st.title("🤖 Free Model Bot via Groq")

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

with st.sidebar:
    st.header("Chat Settings")
    if st.button(" Clear Chat History "):
        # 1. Delete the local persistent JSON file
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        # 2. Reset the session state memory back to defaults
        st.session_state.messages=[{"role": "system", "content": "You are a helpful AI assistant"}]

        # 3. Force Strealit to immediately rerun and refresh the UI blan
        st.rerun()
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
        
        # 1. Call Groq's chat completion with a supported model
        stream_completion = client.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=st.session_state.messages,
            stream=True # <--Tell Grow to send data in chunks

        )

        # 2. Define a generator function to yield text chunks as they arrive
        def generate_chunks():
            for chunk in stream_completion:
                # Safely grab the text content from the chunk delta
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        # 3. Pass the generator directly to streamlit's built-in streaming UI function
        ai_response = st.write_stream(generate_chunks())
        # response_placeholder.write(ai_response)
        
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    save_chat_history(st.session_state.messages)
