# mindful_chat_app.py
import streamlit as st
import google.generativeai as genai # For Gemini API
import os # To potentially use environment variables later

# --- Configuration ---
st.set_page_config(page_title="MindfulChat", page_icon="💬", layout="centered")
st.title("💬 MindfulChat: Your Supportive AI Pal")

# --- CRUCIAL DISCLAIMER ---
st.warning(
    "**Disclaimer:** This is an AI-powered chatbot for demonstration purposes only. "
    "It is NOT a substitute for professional mental health advice, diagnosis, or treatment. "
    "If you need mental health support, please consult a qualified professional or a crisis hotline. "
    "The AI may generate inaccurate or unhelpful responses."
)
st.markdown("---")

# --- API Key Management & Gemini Model Initialization ---
# Using st.session_state to store API key and model only if they are not already there.
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'chat_model' not in st.session_state:
    st.session_state.chat_model = None
if 'chat_session' not in st.session_state:
    st.session_state.chat_session = None

with st.sidebar:
    st.header("API Configuration")
    # Input for API Key
    # In a real app, use st.secrets or environment variables
    # api_key_input = st.secrets.gemini_api_key
    api_key_input = st.text_input("Enter your Google Gemini API Key:", type="password", value=st.session_state.api_key)

    if st.button("Set API Key", key="set_api_key_button"):
        if api_key_input:
            st.session_state.api_key = api_key_input
            try:
                genai.configure(api_key=st.session_state.api_key)
                st.session_state.chat_model = genai.GenerativeModel('gemini-2.0-flash') # Or other suitable model
                # Define the persona and instructions for the model
                # This is a simplified system prompt
                initial_prompt = """
                You are MindfulChat, a friendly and empathetic AI companion.
                Your goal is to provide supportive and understanding responses.
                Listen actively, validate feelings, and offer general, non-medical coping suggestions if appropriate.
                Do NOT provide medical advice, diagnosis, or crisis intervention.
                If the user expresses severe distress or mentions self-harm or harm to others,
                gently state your limitations as an AI and strongly advise them to seek help from a qualified professional
                or a crisis hotline immediately.
                Keep your responses concise and kind. Use emojis where appropriate to convey warmth.
                Start the conversation by warmly greeting the user and asking how they are doing.
                """
                st.session_state.chat_session = st.session_state.chat_model.start_chat(
                    history=[{"role": "user", "parts": [initial_prompt]}, # Priming the model
                             {"role": "model", "parts": ["Hello there! I'm MindfulChat, your supportive AI pal. How are you feeling today? 😊"]}]
                )
                st.success("API Key configured and chat session started!")
                st.info("You can now start chatting in the main window.")
            except Exception as e:
                st.error(f"Failed to configure API or start chat: {e}")
                st.session_state.api_key = "" # Reset if failed
                st.session_state.chat_model = None
                st.session_state.chat_session = None
        else:
            st.warning("Please enter an API Key.")

    if st.session_state.api_key and st.session_state.chat_session:
        st.sidebar.success("Gemini API Ready!")
    else:
        st.sidebar.error("Gemini API Key not configured. Please set it above.")

# --- Initialize chat history in session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add the initial model greeting to the display history if a chat session is active
    if st.session_state.chat_session and st.session_state.chat_session.history:
         # The last message in chat_session.history should be the initial greeting by the model
        if len(st.session_state.chat_session.history) > 1: # Ensure there's a model response after the prompt
            initial_model_message = st.session_state.chat_session.history[-1].parts[0].text
            st.session_state.messages.append({"role": "assistant", "content": initial_model_message})

st.markdown("### Chat with MindfulChat")
# Display existing messages (will be empty initially until API key is set)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Add this code at the end of mindful_chat_app.py

# --- Chat Input and Response Logic ---
user_prompt = st.chat_input("How can I help you feel a bit better today?")

if user_prompt:
    # Add user message to display chat history
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Get response from Gemini if API key and chat session are available
    if st.session_state.api_key and st.session_state.chat_session:
        try:
            with st.spinner("MindfulChat is thinking... 🤔"):
                # Send user message to the existing chat session
                response = st.session_state.chat_session.send_message(user_prompt)
                # The response object itself has the text in response.text
                # or iterate through response.parts if there are multiple
                model_response_text = response.text

            # Add model response to display chat history
            st.session_state.messages.append({"role": "assistant", "content": model_response_text})
            with st.chat_message("assistant"):
                st.markdown(model_response_text)

        except Exception as e:
            st.error(f"Error communicating with Gemini: {e}")
            # Optionally, remove the last user message if the API call failed,
            # or add an error message from the assistant.
            # For simplicity, we'll just show an error.
    else:
        st.error("API Key not configured. Please set it in the sidebar to chat.")
        # Remove the user message from display if API is not configured, as it wasn't processed
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            st.session_state.messages.pop()


# --- (Optional) Add a "Clear Chat" button ---
if st.sidebar.button("Clear Chat History", key="clear_chat"):
    st.session_state.messages = []
    # Also reset the Gemini chat session to start fresh with the initial prompt
    if st.session_state.chat_model:
        initial_prompt = """
        You are MindfulChat, a friendly and empathetic AI companion.
        Your goal is to provide supportive and understanding responses.
        Listen actively, validate feelings, and offer general, non-medical coping suggestions if appropriate.
        Do NOT provide medical advice, diagnosis, or crisis intervention.
        If the user expresses severe distress or mentions self-harm or harm to others,
        gently state your limitations as an AI and strongly advise them to seek help from a qualified professional
        or a crisis hotline immediately.
        Keep your responses concise and kind. Use emojis where appropriate to convey warmth.
        Start the conversation by warmly greeting the user and asking how they are doing.
        """
        st.session_state.chat_session = st.session_state.chat_model.start_chat(
            history=[{"role": "user", "parts": [initial_prompt]},
                     {"role": "model", "parts": ["Hello again! I'm here to listen. How are you feeling right now? 😊"]}]
        )
        # Add the new initial greeting to the display history
        if st.session_state.chat_session and st.session_state.chat_session.history:
            if len(st.session_state.chat_session.history) > 1:
                initial_model_message = st.session_state.chat_session.history[-1].parts[0].text
                st.session_state.messages.append({"role": "assistant", "content": initial_model_message})
        st.rerun() # Rerun to clear the displayed chat
    else:
        st.warning("API Key not configured, cannot clear chat session fully.")