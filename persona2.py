# Change your New Chat initialization from this:
save_chat(new_chat_name, [{"role": "system", "content": "You are a helpful AI assistant."}])

# To this:
save_chat(new_chat_name, [{"role": "system", "content": system_prompt}])
