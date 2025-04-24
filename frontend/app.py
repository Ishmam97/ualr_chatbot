import streamlit as st
import requests
import json

# Page configuration
st.set_page_config(page_title="UALR Chatbot Demo", layout="centered")
st.title("🎓 UALR Q&A Chatbot")

# Sidebar for API key input
st.sidebar.title("⚙️ Options")
api_key = st.sidebar.text_input(
    "Google Gemini API Key", 
    type="password", 
    placeholder="Enter your API key...", 
    key="api_key_input"
)

# Main input for query
query = st.text_input(
    "Ask a question about UALR:", 
    placeholder="Type your question here...", 
    key="query_input"
)
k = 3

# Submit button
if st.button("Submit", key="submit_button"):
    if query and api_key:
        with st.spinner("Fetching response..."):
            try:
                
                payload = {
                    "query": query,
                    "api_key": api_key,
                    "k": k,
                    "model": "gemini-1.5-flash-latest"
                }
                
                
                response = requests.post("http://localhost:8000/query", json=payload)
                response.raise_for_status()
                
                
                result = response.json()
                
                
                with st.expander("🔍 Retrieved Information"):
                    if result.get("retrieved_docs"):
                        for i, doc in enumerate(result["retrieved_docs"], 1):
                            st.markdown(f"**Document {i}**")
                            st.write(doc.get("content", "No content available"))
                    else:
                        st.warning("No relevant documents were retrieved.")
                
                st.markdown("### Answer")
                st.write(result.get("response", "No response returned."))
                
            except requests.exceptions.HTTPError as e:
                st.error(f"Backend error: {e.response.json().get('detail', 'Unknown error')}")
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to backend: {e}")
            except (json.JSONDecodeError, KeyError):
                st.error(f"Received an invalid response from the backend.")
    else:
        st.warning("Please provide both a question and a valid API key.")