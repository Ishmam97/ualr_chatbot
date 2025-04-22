import streamlit as st
from ualr_chatbot.retriever import Retriever
from ualr_chatbot.llm import call_gemini

@st.cache_resource # Use cache_resource for objects like models/connections
def load_retriever():
    """Loads and caches the Retriever instance."""
    st.info("Initializing Retriever (this should only happen once per session)...")
    try:
        # Provide the necessary arguments to your Retriever's __init__
        # IMPORTANT: Make sure 'faiss_index.index' and 'doc_metadata.pkl' paths
        # are accessible from where the Streamlit app runs. Use absolute paths
        # or paths relative to app.py if needed.
        retriever_instance = Retriever(index_path="faiss_index.index", metadata_path="doc_metadata.pkl")
        st.success("Retriever initialized successfully!")
        return retriever_instance
    except FileNotFoundError as e:
        st.error(f"Failed to initialize Retriever: Required file not found. {e}")
        st.error("Ensure 'faiss_index.index' and 'doc_metadata.pkl' exist at the expected location.")
        return None
    except Exception as e:
        st.error(f"Failed to initialize the Retriever: {e}")
        # Display more details for debugging if needed
        # st.exception(e)
        return None 

st.set_page_config(page_title="UALR Chatbot Demo", layout="centered")
st.title("🎓 UALR Q&A Chatbot v2")

query = st.text_input("Ask a question:", placeholder="Type your question here...", key="query_input")

st.sidebar.title("🎓 UALR Chatbot - Options")
api_key = st.sidebar.text_input("Google Gemini API Key", type="password", placeholder="Enter your API key here...")

if query:
    context_docs = retriever.query(query)
    context = "\n\n".join([doc["content"] for doc in context_docs])

    with st.expander("🔍 Looking through info..."):
        st.markdown(context)

    st.markdown("### Answer from LLM")
    final_prompt = f""" You are a helpful chatbot for university of arkansas at little rock, Use the following context to answer the question.\n\nContext:\n{context}\n\nQuestion: {query} \n If you do not find a definite answer to the question in the context, guide the user by providing contact information of who to contact including name email phone number etc if that is available. Ignore any part of the context that is irrelevant. Your output should be like a helpful assistant who guides the user to take the right steps. instead of mentioning the 'provided' text just say, I was unable to find specific information regarding this but here is what you can do ..."""
    response = call_gemini(api_key=api_key,prompt=final_prompt)
    st.write(response)