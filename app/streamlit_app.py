
import streamlit as st

from conversation import InsuranceConversation


# =========================================================
# Page configuration
# =========================================================

st.set_page_config(
    page_title="InsureAssist",
    page_icon="🛡️",
    layout="wide"
)


# =========================================================
# Application title
# =========================================================

st.title("🛡️ InsureAssist")

st.subheader(
    "AI Insurance Policy Purchase Assistant"
)

st.write(
    "Tell me about your insurance needs and "
    "I'll help you find suitable policies."
)


# =========================================================
# Create conversation object
# =========================================================

if "chatbot" not in st.session_state:

    st.session_state.chatbot = (
        InsuranceConversation()
    )


# =========================================================
# Display current customer profile
# =========================================================

with st.sidebar:

    st.header("Customer Profile")

    profile = (
        st.session_state.chatbot.get_profile()
    )

    if profile:

        if "age" in profile:
            st.write(
                f"**Age:** {profile['age']}"
            )

        if "budget" in profile:
            st.write(
                f"**Annual Budget:** "
                f"₹{profile['budget']:,}"
            )

        if "required_coverage" in profile:
            st.write(
                f"**Required Coverage:** "
                f"₹{profile['required_coverage']:,}"
            )

        if "maternity_required" in profile:

            maternity = (
                "Yes"
                if profile["maternity_required"]
                else "No"
            )

            st.write(
                f"**Maternity:** {maternity}"
            )

        if "pre_existing_disease" in profile:

            existing = (
                "Yes"
                if profile["pre_existing_disease"]
                else "No"
            )

            st.write(
                f"**Pre-existing Disease:** {existing}"
            )

        if "max_deductible" in profile:

            st.write(
                f"**Maximum Deductible:** "
                f"₹{profile['max_deductible']:,}"
            )

        if "max_waiting_period_years" in profile:

            st.write(
                f"**Max Waiting Period:** "
                f"{profile['max_waiting_period_years']:.1f} years"
            )

    else:

        st.info(
            "Your profile will appear here "
            "as we chat."
        )


# =========================================================
# Reset conversation
# =========================================================

if st.sidebar.button("🔄 Start New Conversation"):

    st.session_state.chatbot = (
        InsuranceConversation()
    )

    st.rerun()


# =========================================================
# Display conversation history
# =========================================================

history = (
    st.session_state.chatbot.history
)

for message in history:

    role = message["role"]

    if role == "customer":

        with st.chat_message("user"):

            st.write(
                message["message"]
            )

    else:

        with st.chat_message("assistant"):

            st.write(
                message["message"]
            )


# =========================================================
# Chat input
# =========================================================

user_message = st.chat_input(
    "Tell me about your insurance needs..."
)


# =========================================================
# Process customer message
# =========================================================

if user_message:

    with st.chat_message("user"):

        st.write(user_message)

    response = (
        st.session_state.chatbot
        .process_message(user_message)
    )

    with st.chat_message("assistant"):

        st.write(response)

    st.rerun()

