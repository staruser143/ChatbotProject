# --- STEP 1: DEFINE PRESETS ---
PERSONAS = {
    "Standard": "You are a helpful, direct, and concise AI assistant.",
    "Python Mentor": "You are an expert Python tutor. Always explain code step-by-step using beginner-friendly analogies and best practices.",
    "Creative Writer": "You are a poetic, expressive novelist. Use vivid imagery, metaphors, and highly descriptive text.",
    "Pirate": "Ahoy! You are a salty pirate captain. Answer every prompt using pirate slang, sea jargon, and enthusiastic expressions like 'Arr matey!'."
}

with st.sidebar:
    st.header("💬 Conversations")
    # ... (keep your existing "New Chat" and dropdown code here) ...
    
    st.markdown("---")
    st.header("🎭 Persona")
    
    # STEP 2: ADD DROPDOWN TO SELECT PERSONA
    selected_persona = st.selectbox("Choose AI Persona:", list(PERSONAS.keys()))
    system_prompt = PERSONAS[selected_persona]
