import os
os.environ["STREAMLIT_SERVER_ENABLE_FILE_WATCHER"] = "false"
import streamlit as st

st.set_page_config(page_title="UALR Chatbot Demo", layout="centered")
st.title("🎓 UALR Q&A Chatbot v2")


base_path = os.path.dirname(__file__)
index_path = os.path.join(base_path, "faiss_index.index")
metadata_path = os.path.join(base_path, "doc_metadata.pkl")



if "retriever_instance" not in st.session_state:
    retriever_instance = Retriever(index_path=index_path, metadata_path=metadata_path)
    st.session_state["retriever_instance"] = retriever_instance


query = st.text_input("Ask a question:", placeholder="Type your question here...", key="query_input")

st.sidebar.title("🎓 UALR Chatbot - Options")
api_key = st.sidebar.text_input("Google Gemini API Key", type="password", placeholder="Enter your API key here...")

if query:
    context_docs = retriever_instance.query(query)
    context = "\n\n".join([doc["content"] for doc in context_docs])

    with st.expander("🔍 Looking through info..."):
        st.markdown(context)

    st.markdown("### Answer from LLM")
    final_prompt = f""" You are a helpful chatbot for university of arkansas at little rock, Use the following context to answer the question.\n\nContext:\n{context}\n\nQuestion: {query} \n If you do not find a definite answer to the question in the context, guide the user by providing contact information of who to contact including name email phone number etc if that is available. Ignore any part of the context that is irrelevant. Your output should be like a helpful assistant who guides the user to take the right steps. instead of mentioning the 'provided' text just say, I was unable to find specific information regarding this but here is what you can do ..."""
    response = call_gemini(api_key=api_key,prompt=final_prompt)
    st.write(response)