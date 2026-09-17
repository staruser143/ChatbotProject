    # 1. RAG LOOKUP
    search_results = db.similarity_search(user_input, k=2)
    context_text = "\n".join([doc.page_content for doc in search_results])
    
    # 2. SYSTEM INJECTION (This dynamically replaces the persona system prompt)
    rag_system_prompt = (
        "You are a helpful data assistant. Use ONLY the following pieces of context to answer the question. "
        "If you don't know the answer based on this context, say 'I cannot find that in my database.'\n\n"
        f"--- CONTEXT ---\n{context_text}\n-----------"
    )
    
    # 3. BUILD CLEAN API PAYLOAD
    # We strip out any old system prompts stored in active_messages to avoid duplicates
    clean_history = [msg for msg in active_messages if msg["role"] != "system"]
    
    payload = [{"role": "system", "content": rag_system_prompt}] + clean_history
    payload.append({"role": "user", "content": user_input})
