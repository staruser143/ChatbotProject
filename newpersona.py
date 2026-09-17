import json
import os
import streamlit as st
from groq import Groq

st.title("🎭 Persona-Based Multi-Chat Bot")

CHATS_DIR = "saved_chats"
os.makedirs(CHATS_DIR, exist_ok=True)
client = Groq()

# --- PERSONA DICTIONARY CONFIGURATION ---
PERSONAS = {
    "🤖 Standard Assistant": "You are a helpful, direct, and concise AI assistant.",
    "🐍 Python Mentor": "You are an expert programming tutor. Explain code step-by-step using beginner-friendly python analogies and clean PEP-8 best practices.",
    "✍️ Creative Writer": "You are a poetic, highly descriptive novelist. Use vivid imagery, metaphors, and storytelling elements.",
    "🏴‍☠️ Pirate Captain": "Ahoy! You are a salty pirate captain. Answer every prompt using pirate slang, sea jargon, and enthusiastic expressions like 'Arr matey!'."
}

def get_all_chats():
    files = [f for f in os.listdir(CHATS_DIR) if f.endswith(".json")]
    return [f.replace(".json", "") for f in files]

def load_chat(chat_name):
    file_path = os.path.join(CHATS_DIR, f"{chat_name}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return [{"role": "system", "content": PERSONAS["🤖 Standard Assistant"]}]

def save_chat(chat_name, messages):
    file_path = os.path.join(CHATS_DIR, f"{chat_name}.json")
    with open(file_path, "w") as f:
        json.dump(messages, f, indent=4)

def auto_rename_chat(current_name, user_first_message):
    try:
        rename_prompt = (
            f"Summarize this user question into a short topic name of exactly 2 to 3 words. "
            f"Do not include quotes, periods, introduction text, or newlines. Just the title itself.\n"
            f"Question: '{user_first_message}'"
        )
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": rename_prompt}],
            stream=False
        )
        
        new_title = response.choices[0].message.content.strip()
        new_title = new_title.replace('"', '').replace("'", "").replace("\n", "").replace("\r", "")
        
        for char in ['/', '\\', '?', '%', '*', ':', '|', '"', '<', '>', '.']:
            new_title = new_title.replace(char, '')
            
        new_title = " ".join(new_title.split()[:4])
        
        if not new_title or len(new_title.strip()) == 0:
            return

        old_path = os.path.join(CHATS_DIR, f"{current_name}.json")
        new_path = os.path.join(CHATS_DIR, f"{new_title}.json")
        
        if os.path.exists(new_path):
            new_title = f"{new_title} New"
            new_path = os.path.join(CHATS_DIR, f"{new_title}.json")

        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            st.session_state.current_chat = new_title
            
    except Exception as e:
        print(f"DEBUG ERROR RENAME FAILED: {str(e)}")

# --- SIDEBAR COMPONENT ---
with st.sidebar:
    st.header("🎭 Persona Selection")
    # Users select the persona *before* clicking New Chat
    chosen_persona_key = st.selectbox("Select Persona for New Chats:", list(PERSONAS.keys()))
    selected_system_prompt = PERSONAS[chosen_persona_key]

    st.markdown("---")
    st.header("💬 Conversations")
    
    if st.button("➕ New Chat", use_container_width=True):
        all_chats = get_all_chats()
        new_chat_number = len(all_chats) + 1
        new_chat_name = f"Chat {new_chat_number}"
        
        # FIXED: Initialize the new file using the dynamic system prompt chosen from the dropdown
        save_chat(new_chat_name, [{"role": "system", "content": selected_system_prompt}])
        st.session_state.current_chat = new_chat_name
        st.rerun()

    chat_options = get_all_chats()
    if not chat_options:
        save_chat("Default Chat", [{"role": "system", "content": PERSONAS["🤖 Standard Assistant"]}])
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
            save_chat("Default Chat", [{"role": "system", "content": PERSONAS["🤖 Standard Assistant"]}])
        st.rerun()

# --- MAIN CHAT INTERFACE ---
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

    # --- AUTO-RENAME TRIGGER ---
    is_generic_name = st.session_state.current_chat.startswith("Chat ") or st.session_state.current_chat == "Default Chat"
    if is_generic_name and len(active_messages) == 3:
        first_prompt = active_messages[1]["content"]
        auto_rename_chat(st.session_state.current_chat, first_prompt)
        st.rerun()
