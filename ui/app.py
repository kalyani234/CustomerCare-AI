
from pathlib import Path

import streamlit as st
from chatbot.llm import generate_response


# Page configuration
st.set_page_config(
    page_title="CustomerCare AI",
    page_icon="🤖",
    layout="centered"
)

# Image path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
HERO_IMAGE = PROJECT_ROOT / "assets" / "customer_support_hero.png"


# Simple blue theme
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #061A40, #123F78);
    color: white;
}

h1, h2, h3, p, label {
    color: white !important;
}

div[data-testid="stChatMessage"] {
    background-color: #164B87;
    border-radius: 10px;
}

div[data-testid="stChatInput"] {
    background-color: #164B87;
    border: 1px solid #60A5FA;
    border-radius: 10px;
}

div[data-testid="stChatInput"] textarea {
    color: white !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: #D6E8FF !important;
}

.stButton button {
    background-color: #2563EB;
    color: white;
    border-radius: 8px;
}

.footer {
    text-align: center;
    color: #D6E8FF;
    font-size: 13px;
    padding: 15px;
}
</style>
""", unsafe_allow_html=True)


# Hero image
if HERO_IMAGE.exists():
    st.image(str(HERO_IMAGE), use_container_width=True)


# Application heading
st.title("🤖 CustomerCare AI")

st.markdown(
    "Your AI-powered customer support assistant. "
    "Ask questions about delivery, returns and products."
)

st.divider()


# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Clear chat
col1, col2 = st.columns([4, 1])

with col2:
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()


# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Customer input
question = st.chat_input(
    "Ask me about delivery, returns or products..."
)


# Generate chatbot response
if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner("CustomerCare AI is thinking..."):

            try:
                answer = generate_response(question)

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception:
                st.error(
                    "Sorry, something went wrong. Please try again."
                )


# Footer
st.divider()

st.markdown("""
<div class="footer">
    CustomerCare AI | Powered by Groq, RAG and Python
    <br>
    AI Customer Support Quality Engineering Project
</div>
""", unsafe_allow_html=True)
