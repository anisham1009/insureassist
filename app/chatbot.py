import sys
import os

import streamlit as st


# ============================================================
# Add app directory to Python path
# ============================================================

APP_DIR = os.path.dirname(os.path.abspath(__file__))

if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)


from conversation import ConversationManager


# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="InsureAssist",
    page_icon="🏥",
    layout="centered"
)


# ============================================================
# Title
# ============================================================

st.title("🏥 InsureAssist")

st.write(
    "Your AI assistant for health insurance "
    "policy questions and recommendations."
)


# ============================================================
# Create conversation manager
# ============================================================

if "conversation" not in st.session_state:

    st.session_state.conversation = ConversationManager()


conversation = st.session_state.conversation


# ============================================================
# Chat history
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# Display previous messages

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ============================================================
# User input
# ============================================================

user_message = st.chat_input(
    "Ask about health insurance..."
)


if user_message:

    # --------------------------------------------------------
    # Display customer message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    with st.chat_message("user"):

        st.markdown(user_message)


    # --------------------------------------------------------
    # Process message
    # --------------------------------------------------------

    try:

        answer = conversation.process_message(
            user_message
        )

    except Exception as e:

        answer = (
            "Sorry, I encountered an error while "
            "processing your question.\n\n"
            f"Error: `{e}`"
        )


    # --------------------------------------------------------
    # Display assistant response
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    with st.chat_message("assistant"):

        st.markdown(answer)