import streamlit as st
from ualr_chatbot.retriever import Retriever
from ualr_chatbot.llm import call_ollama

# Load components
retriever = Retriever("faiss_index.index", "doc_metadata.pkl")

st.set_page_config(page_title="UALR Chatbot Demo", layout="centered")
st.title("🎓 UALR Q&A Chatbot")

query = st.text_input("Ask a question:")

if query:
    context_docs = retriever.query(query)
    context = "\n\n".join([doc["content"] for doc in context_docs])

    with st.expander("🔍 Looking through info..."):
        st.markdown(context)

    st.markdown("### Answer from LLM")
    final_prompt = f"""Use the following context to answer the question.\n\nContext:\n{context}\n\nQuestion: {query} \n If you do not find a definite answer to the question provide contact information of who to contact including name email phone number etc if that is available. Ignore any part of the context that is irrelevant"""
    response = call_ollama(final_prompt)
    st.write(response)