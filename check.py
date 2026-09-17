    active_messages.append({"role": "assistant", "content": ai_response})
    save_chat(st.session_state.current_chat, active_messages)

    # --- FIXED AUTO-RENAME TRIGGER ---
    is_generic_name = st.session_state.current_chat.startswith("Chat ") or st.session_state.current_chat == "Default Chat"
    
    # turn 1 = system prompt (index 0) + user msg (index 1) + assistant msg (index 2) = 3 total items
    if is_generic_name and len(active_messages) == 3:
        # CORRECTED: Access index 1 to fetch the user's first question string [1]
        first_prompt = active_messages[1]["content"] 
        auto_rename_chat(st.session_state.current_chat, first_prompt)
        st.rerun() 
