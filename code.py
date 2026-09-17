import json
import os
import streamlit as st
from groq import Groq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

st.title("📂 Knowledge Base Bot (RAG)")

CHATS_DIR = "saved_chats"
os.makedirs(CHATS_DIR, exist_ok=True)
client = Groq()

# --- INITIALIZE DATABASE ACCESS ---
# Load the database folder we generated using ingest.py
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma(persist_directory="chroma_db", embedding_function=embeddings)

def get_all_chats():
    files = [f for f in os.listdir(CHATS_DIR) if f.endswith(".json")]
    return [f.replace(".json", "") for f in files]

def load_chat(chat_name):
    file_path = os.path.join(CHATS_DIR, f"{chat_name}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return []

def save_chat(chat_name, messages):
    file_path = os.path.join(CHATS_DIR, f"{chat_name}.json")
    with open(file_path, "w") as f:
        json.dump(messages, f, indent=4)

# --- SIDEBAR OUTLINE ---
with st.sidebar:
    st.header("💬 Conversations")
    if st.button("➕ New Chat", use_container_width=True):
        all_chats = get_all_chats()
        new_chat_name = f"Chat {len(all_chats) + 1}"
        save_chat(new_chat_name, [])
        st.session_state.current_chat = new_chat_name
        st.rerun()

    chat_options = get_all_chats()
    if not chat_options:
        save_chat("Default Chat", [])
        chat_options = ["Default Chat"]

    if "current_chat" not in st.session_state or st.session_state.current_chat not in chat_options:
        st.session_state.current_chat = chat_options

    st.session_state.current_chat = st.selectbox(
        "Select Active Chat:", options=chat_options, index=chat_options.index(st.session_state.current_chat)
    )

# --- MAIN DISPLAY ENGINE ---
active_messages = load_chat(st.session_state.current_chat)

for message in active_messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

if user_input := st.chat_input("Ask something about Project Nebula..."):
    with st.chat_message("user"):
        st.write(user_input)
    
    # 1. RAG LOOKUP: Query Chroma to extract relevant context from knowledge.txt
    search_results = db.similarity_search(user_input, k=2)
    context_text = "\n".join([doc.page_content for doc in search_results])
    
    # 2. SYSTEM INJECTION: Construct a prompt forcing the bot to use the text context
    rag_system_prompt = (
        "You are a helpful data assistant. Use ONLY the following pieces of context to answer the question. "
        "If you don't know the answer based on this context, say 'I cannot find that in my database.'\n\n"
        f"--- CONTEXT ---\n{context_text}\n-----------"
    )
    
    # 3. BUILD API PAYLOAD: Inject the system prompt at the beginning of the chat log
    payload = [{"role": "system", "content": rag_system_prompt}] + active_messages
    payload.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        stream_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=payload,
            stream=True
        )
        
        def generate_chunks():
            for chunk in stream_completion:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        ai_response = st.write_stream(generate_chunks())
        
    # Append turns to history list and save
    active_messages.append({"role": "user", "content": user_input})
    active_messages.append({"role": "assistant", "content": ai_response})
    save_chat(st.session_state.current_chat, active_messages)
