    # --- FIXED: Safe Dropdown Index Lookup ---
    # Find the correct index position, defaulting to 0 if the chat isn't in the list yet
    if "current_chat" in st.session_state and st.session_state.current_chat in chat_options:
        default_index = chat_options.index(st.session_state.current_chat)
    else:
        default_index = 0

    # Render the selectbox safely using our calculated index
    st.session_state.current_chat = st.selectbox(
        "Select Active Chat:", 
        options=chat_options, 
        index=default_index
    )
