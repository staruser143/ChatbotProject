import json
import os
import streamlit as st
from groq import Groq

st.title("🤖 Multi-Chat Assistant via Groq")

CHATS_DIR = "saved_chats"
os.makedirs(CHATS_DIR, exist_ok=True)
client = Groq()

def get_all_chats():
    files = [f for f in os.listdir(CHATS_DIR) if f.endswith(".json")]
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

# --- NEW: AUTO-RENAME HELPER FUNCTION ---
def auto_rename_chat(current_name, user_first_message):
    """Asks Llama to generate a 3-word title based on the first message."""
    try:
        rename_prompt = (
            f"Analyze this user message and generate a concise conversation title "
            f"that is 2 to 3 words long maximum. Do not use quotes, punctuation, or extra text. "
            f"Message: '{user_first_message}'"
        )
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": rename_prompt}],
            stream=False # Keep stream false here for a quick, direct response
        )
        
        # Clean up the output title
        new_title = response.choices[0].message.content.strip().replace('"', '')
        
        # Sanitize filename (remove characters that OS file systems dislike)
        for char in ['/', '\\', '?', '%', '*', ':', '|', '"', '<', '>']:
            new_title = new_title.replace(char, '')
            
        if new_title:
            old_path = os.path.join(CHATS_DIR, f"{current_name}.json")
            new_path = os.path.join(CHATS_DIR, f"{new_title}.json")
            
            # Rename the file on disk and update session state
            os.rename(old_path, new_path)
            st.session_state.current_chat = new_title
    except Exception as e:
        # Fallback silently if the API call fails so it doesn't crash the main chat
        pass
# ----------------------------------------

with st.sidebar:
    st.header("💬 Conversations")
    
    if st.button("➕ New Chat", use_container_width=True):
        all_chats = get_all_chats()
        new_chat_number = len(all_chats) + 1
        new_chat_name = f"Chat {new_chat_number}"
        
        save_chat(new_chat_name, [{"role": "system", "content": "You are a helpful AI assistant."}])
        st.session_state.current_chat = new_chat_name
        st.rerun()

    chat_options = get_all_chats()
    if not chat_options:
        save_chat("Default Chat", [{"role": "system", "content": "You are a helpful AI assistant."}])
        chat_options = ["Default Chat"]

    if "current_chat" not in st.session_state or st.session_state.current_chat not in chat_options:
        st.session_state.current_chat = chat_options[0]

    selected_chat = st.selectbox(
        "Select Active Chat:",
        options=chat_options,
        index=chat_options.index(st.session_state.current_chat)
    )
    
    if selected_chat != st.session_state.current_chat:
        st.session_state.current_chat = selected_chat
        st.rerun()

    st.markdown("---")
    st.header("Settings")
    
    if st.button("🗑️ Delete Current Chat", use_container_width=True):
        file_to_delete = os.path.join(CHATS_DIR, f"{st.session_state.current_chat}.json")
        if os.path.exists(file_to_delete):
            os.remove(file_to_delete)
        
        remaining_chats = get_all_chats()
        if remaining_chats:
            st.session_state.current_chat = remaining_chats[0]
        else:
            st.session_state.current_chat = "Default Chat"
            save_chat("Default Chat", [{"role": "system", "content": "You are a helpful AI assistant."}])
        st.rerun()

active_messages = load_chat(st.session_state.current_chat)

for message in active_messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

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
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        ai_response = st.write_stream(generate_chunks())
        
    active_messages.append({"role": "assistant", "content": ai_response})
    save_chat(st.session_state.current_chat, active_messages)

    # --- NEW: TRIGGER AUTO-RENAME ---
    # We check if the chat name starts with "Chat " or "Default Chat" 
    # AND ensure this is the very first turn (system prompt + 1 user msg + 1 assistant msg = 3 total)
    is_generic_name = st.session_state.current_chat.startswith("Chat ") or st.session_state.current_chat == "Default Chat"
    if is_generic_name and len(active_messages) == 3:
        # Extract the original first prompt from the conversation list
        first_prompt = active_messages[1]["content"] 
        auto_rename_chat(st.session_state.current_chat, first_prompt)
        st.rerun() # Refresh screen to update the sidebar dropdown layout immediately
