import json
import os
import streamlit as st
from groq import Groq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

st.title("📂 Custom Knowledge Base Chatbot (RAG)")

client = Groq()

# Initialize embeddings and load the database we created in step 3
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = Chroma(persist_directory="chroma_db", embedding_function=embeddings)

# [Keep your standard load_chat, save_chat, and sidebar UI logic from previous steps here]

# --- MAIN CHAT LOOP WITH RAG AUGMENTATION ---
if user_input := st.chat_input("Ask me about Project Nebula..."):
    # Display user input
    with st.chat_message("user"):
        st.write(user_input)
    
    # 1. SEARCH THE KNOWLEDGE BASE: Fetch the 2 most relevant chunks matching the prompt
    search_results = db.similarity_search(user_input, k=2)
    retrieved_context = "\n".join([doc.page_content for doc in search_results])
    
    # 2. INJECT KNOWLEDGE: Format the hidden background payload
    rag_system_prompt = (
        f"You are a helpful assistant. Use ONLY the following pieces of custom context to answer the question. "
        f"If you do not know the answer based on this data, say 'I cannot find that in the custom database'.\n\n"
        f"--- CUSTOM CONTEXT ---\n{retrieved_context}\n----------------------"
    )
    
    # Construct the message payload combining background knowledge + history
    active_messages = [{"role": "system", "content": rag_system_prompt}]
    # Append user input...
    active_messages.append({"role": "user", "content": user_input})

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
        
    # (Save your text outputs to your historical JSON lists as normal)
