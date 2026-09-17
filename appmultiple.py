import json
import os
import streamlit as st
from groq import Groq

st.title("🤖 Multi-Chat Assistant via Groq")

# 1. Setup a dedicated directory to store all chats
CHATS_DIR = "saved_chats"
os.makedirs(CHATS_DIR, exist_ok=True)
client = Groq()

# --- HELPER FUNCTIONS FOR FILE OPERATIONS ---
def get_all_chats():
    """Returns a list of chat names sorted by creation time."""
    files = [f for f in os.listdir(CHATS_DIR) if f.endswith(".json")]
    # Sort files so newer ones appear or match directory order
    return [f.replace(".json", "") for f in files]

def load_chat(chat_name):
    file_path = os.path.join(CHATS_DIR, f"{chat_name}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return [{"role": "system", "content": "You are a helpful AI assistant."}]

def save_chat(chat_name, messages):
    file_path = os.path.join(CHATS_DIR, f"{chat_name}.json")
    with open(file_path, "w") as f:
        json.dump(messages, f, indent=4)

# --- SIDEBAR: MULTI-CHAT MANAGEMENT ---
with st.sidebar:
    st.header("💬 Conversations")
    
    # Button to create a brand new conversation
    if st.button("➕ New Chat", use_container_width=True):
        all_chats = get_all_chats()
        new_chat_number = len(all_chats) + 1
        new_chat_name = f"Chat {new_chat_number}"
        
        # Initialize the new file with default system prompt
        save_chat(new_chat_name, [{"role": "system", "content": "You are a helpful AI assistant."}])
        st.session_state.current_chat = new_chat_name
        st.rerun()

    # Get updated list of chats for the dropdown selector
    chat_options = get_all_chats()
    if not chat_options:
        # Default fallback if directory is completely empty
        save_chat("Default Chat", [{"role": "system", "content": "You are a helpful AI assistant."}])
        chat_options = ["Default Chat"]

    # Keep track of active chat in session state
    if "current_chat" not in st.session_state or st.session_state.current_chat not in chat_options:
        st.session_state.current_chat = chat_options[0]

    # Dropdown menu to switch conversations
    selected_chat = st.selectbox(
        "Select Active Chat:",
        options=chat_options,
        index=chat_options.index(st.session_state.current_chat)
    )
    
    # Handle chat switching
    if selected_chat != st.session_state.current_chat:
        st.session_state.current_chat = selected_chat
        st.rerun()

    st.markdown("---")
    st.header("Settings")
    
    # Delete the currently selected chat
    if st.button("🗑️ Delete Current Chat", use_container_width=True):
        file_to_delete = os.path.join(CHATS_DIR, f"{st.session_state.current_chat}.json")
        if os.path.exists(file_to_delete):
            os.remove(file_to_delete)
        
        # Force switch back to whatever chat is left
        remaining_chats = get_all_chats()
        if remaining_chats:
            st.session_state.current_chat = remaining_chats[0]
        else:
            st.session_state.current_chat = "Default Chat"
            save_chat("Default Chat", [{"role": "system", "content": "You are a helpful AI assistant."}])
        st.rerun()

# --- MAIN CHAT INTERFACE ---
# Load messages dynamically based on which chat is currently active
active_messages = load_chat(st.session_state.current_chat)

# Render historical messages
for message in active_messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Process new prompt
if user_input := st.chat_input("Type your message here..."):
    with st.chat_message("user"):
        st.write(user_input)
    active_messages.append({"role": "user", "content": user_input})
    save_chat(st.session_state.current_chat, active_messages)

    with st.chat_message("assistant"):
        stream_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=active_messages,
            stream=True
        )
        
        def generate_chunks():
            for chunk in stream_completion:
                if chunk.choices.delta.content is not None:
                    yield chunk.choices.delta.content

        ai_response = st.write_stream(generate_chunks())
        
    active_messages.append({"role": "assistant", "content": ai_response})
    save_chat(st.session_state.current_chat, active_messages)
