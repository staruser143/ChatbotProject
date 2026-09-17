# --- UPDATED ROBUST AUTO-RENAME FUNCTION ---
def auto_rename_chat(current_name, user_first_message):
    """Asks Llama to generate a short title, cleans it, and updates file logs securely."""
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
        
        # 1. Clean out white spaces, newlines, quotes, and punctuation completely
        new_title = response.choices[0].message.content.strip()
        new_title = new_title.replace('"', '').replace("'", "").replace("\n", "").replace("\r", "")
        
        # 2. Strip out standard forbidden file characters
        for char in ['/', '\\', '?', '%', '*', ':', '|', '"', '<', '>', '.']:
            new_title = new_title.replace(char, '')
            
        # 3. Cut down length if the AI ignored instructions and wrote a sentence
        new_title = " ".join(new_title.split()[:4])
        
        # Fallback if cleaning leaves it blank
        if not new_title or len(new_title.strip()) == 0:
            return

        old_path = os.path.join(CHATS_DIR, f"{current_name}.json")
        new_path = os.path.join(CHATS_DIR, f"{new_title}.json")
        
        # 4. Check if the new title file already exists to avoid overwriting errors
        if os.path.exists(new_path):
            new_title = f"{new_title} New"
            new_path = os.path.join(CHATS_DIR, f"{new_title}.json")

        # 5. Execute OS rename operation safely
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            # Sync the session memory state immediately to the new name string
            st.session_state.current_chat = new_title
            
    except Exception as e:
        # If something breaks, print it out cleanly in the Codespace terminal logs to see why
        print(f"DEBUG ERROR RENAME FAILED: {str(e)}")
# ----------------------------------------
