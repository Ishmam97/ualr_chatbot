import streamlit as st
import requests
import json
import os
from datetime import datetime
from streamlit_feedback import streamlit_feedback
from langsmith import Client
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
st.set_page_config(page_title="UALR Chatbot Demo", layout="centered")

# Get the API URL from environment variable or use default
API_URL = os.environ.get("API_URL", "http://backend:8000")

# Page configuration
st.title("🎓 UALR Q&A Chatbot")

# Sidebar for API key and model selection
st.sidebar.title("⚙️ Options")
api_key = st.sidebar.text_input(
    "Google Gemini API Key",
    type="password",
    placeholder="Enter your API key...",
    key="api_key_input"
)

# Model selection
model = st.sidebar.selectbox(
    "Model",
    ["gemini-1.5-flash-latest", "gemini-1.5-pro-latest", "gemini-1.0-pro"],
    index=0
)

# Number of documents to retrieve
k = 5

# Display API connection info
with st.sidebar.expander("Connection Info"):
    st.write(f"API URL: {API_URL}")
    if st.button("Test Connection"):
        try:
            response = requests.get(f"{API_URL}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ Connected to backend API")
            else:
                st.error(f"❌ API returned status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Failed to connect: {e}")

# Sidebar form for reporting unanswered questions
st.sidebar.markdown("---")
st.sidebar.markdown("### Report an Unanswered Question")
with st.sidebar.form(key="unanswered_question_form"):
    unanswered_query = st.text_input("What question could the chatbot not answer?")
    correct_answer_suggestion = st.text_area("What is the correct answer or what should it have said?")
    submit_suggestion = st.form_submit_button("Submit Suggestion")
    if submit_suggestion:
        if submit_suggestion:
            if unanswered_query and correct_answer_suggestion:
                feedback_payload = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "query": unanswered_query,
                    "response": None,  # No specific chatbot response is being rated here
                    "feedback_type": "correction_suggestion",
                    "corrected_question": unanswered_query,
                    "correct_answer": correct_answer_suggestion,
                    "model_used": model,  # Current model selection from sidebar
                }
                try:
                    print(f"Submitting correction suggestion: {feedback_payload}")
                    response = requests.post(f"{API_URL}/feedback", json=feedback_payload, timeout=10)
                    response.raise_for_status()  # Check for HTTP errors
                    st.sidebar.success("Suggestion submitted. Thank you!")
                except requests.exceptions.RequestException as e:
                    st.sidebar.error(f"Failed to submit suggestion: {e}")
            else:
                st.sidebar.warning("Please fill in both the question and the suggested answer.")

# Initialize session state for messages and feedback tracking
if "messages" not in st.session_state:
    st.session_state.messages = []
if "feedback_states" not in st.session_state:
    st.session_state.feedback_states = {} # To store feedback status for each message_id

# Display chat messages from history
for i, msg_data in enumerate(st.session_state.messages):
    with st.chat_message(msg_data["role"]):
        st.markdown(msg_data["content"])

        if msg_data["role"] != "assistant":
            continue

        # Ensure message_id exists
        message_id = msg_data.setdefault("message_id", f"asst_fallback_{i}_{datetime.utcnow().timestamp()}")
        feedback_key = f"feedback_{message_id}"

        # Initialize feedback_states if missing
        st.session_state.setdefault("feedback_states", {})

        # Feedback already submitted
        if feedback_key in st.session_state.feedback_states:
            score_display = st.session_state.feedback_states.get(feedback_key, "✅")
            st.markdown(f"<small>Feedback: {score_display} (submitted)</small>", unsafe_allow_html=True)
            continue

        # Show feedback widget
        feedback = streamlit_feedback(
            feedback_type="thumbs",
            optional_text_label="[Optional] Explain your feedback",
            key=feedback_key,
        )

        if not feedback:
            continue

        # Store feedback to prevent resubmission
        st.session_state.feedback_states[feedback_key] = feedback["score"]

        # Determine feedback details
        is_thumbs_up = feedback["score"] == "👍"
        feedback_type_val = "thumbs_up" if is_thumbs_up else "thumbs_down"
        reason_field = "thumbs_up_reason" if is_thumbs_up else "thumbs_down_reason"

        # Build payload
        feedback_payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": msg_data.get("query", "Unknown query (feedback)"),
            "response": msg_data["content"],
            "feedback_type": feedback_type_val,
            reason_field: feedback.get("text"),
            "model_used": msg_data.get("model_used", "Unknown model"),
            "source_message_id": message_id,
            "run_id": msg_data.get("run_id")  # ✅ Include LangSmith run_id
        }

        print(f"Submitting feedback payload: {feedback_payload}")

        # Submit feedback to backend
        try:
            api_response = requests.post(f"{API_URL}/feedback", json=feedback_payload, timeout=10)
            api_response.raise_for_status()
            st.toast(f"Feedback ({feedback['score']}) submitted. Thank you!", icon="✅")
            st.rerun()
        except requests.exceptions.HTTPError as http_err:
            st.error(f"API error submitting feedback: {http_err}")
            st.session_state.feedback_states.pop(feedback_key, None)
        except requests.exceptions.RequestException as req_err:
            st.error(f"Connection error submitting feedback: {req_err}")
            st.session_state.feedback_states.pop(feedback_key, None)


# Chat input for user queries
if prompt := st.chat_input("Ask a question about UALR:"):
    if not api_key:
        st.error("Please provide a valid API key in the sidebar.")
    else:
        # Add user message to chat history
        user_message_timestamp = datetime.utcnow().isoformat()
        user_msg_id = f"user_{user_message_timestamp}_{len(st.session_state.messages)}"
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "message_id": user_msg_id
        })

        with st.spinner("Thinking..."):
            try:
                payload = {
                    "query": prompt,
                    "api_key": api_key,
                    "k": k,
                    "model": model
                }
                response = requests.post(f"{API_URL}/query", json=payload, timeout=60)
                response.raise_for_status()
                result = response.json()

                response_dict = result.get("response", {})
                assistant_response_content = response_dict.get("content", "Sorry, I could not generate a response.")
                retrieved_docs = result.get("retrieved_docs", [])
                run_id = result.get("run_id", None)

                assistant_message_timestamp = datetime.utcnow().isoformat()
                assistant_msg_id = f"asst_{assistant_message_timestamp}_{len(st.session_state.messages)}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_response_content,
                    "query": prompt,
                    "retrieved_docs": retrieved_docs,
                    "model_used": model,
                    "message_id": assistant_msg_id,
                    "run_id": run_id
                })
                logger.info(f"Query response stored with run_id: {run_id}")
                st.rerun()

            except requests.exceptions.HTTPError as e:
                error_msg = f"{e.response.status_code}: {e.response.text}"
                try:
                    error_detail = e.response.json().get('detail', error_msg)
                    error_msg = f"{e.response.status_code}: {error_detail}"
                except json.JSONDecodeError:
                    pass
                st.error(f"Backend error: {error_msg}")
                logger.error(f"Backend error: {error_msg}")
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to backend: {e}")
                logger.error(f"Failed to connect to backend: {e}")
            except (json.JSONDecodeError, KeyError) as e:
                st.error(f"Received an invalid response from the backend: {e}")
                logger.error(f"Invalid backend response: {e}")