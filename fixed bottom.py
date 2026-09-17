    active_messages.append({"role": "assistant", "content": ai_response})
    save_chat(st.session_state.current_chat, active_messages)

    # --- THE TRIGGER BLOCK ---
    is_generic_name = st.session_state.current_chat.startswith("Chat ") or st.session_state.current_chat == "Default Chat"
    
    # Run ONLY when there is exactly 1 user question and 1 AI reply stored
    if is_generic_name and len(active_messages) == 3:
        first_prompt = active_messages[1]["content"]
        auto_rename_chat(st.session_state.current_chat, first_prompt)
        st.rerun()
