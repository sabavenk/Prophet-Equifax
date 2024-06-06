import streamlit as st
import openai
from utils import process_query, pages, SYSTEM_PROMPT

# Streamlit app layout
st.title("SecOps Q/A Chatbot")
st.write("Ask questions about Equifax's cybersecurity breach in 2017 and get detailed responses.")

user_query = st.text_input("Enter your query:")

# Adding model selection and context usage options
model_options = ["gpt-3.5-turbo", "gpt-4o"]
selected_model = st.selectbox("Choose the model:", model_options)
show_context = st.checkbox("Show context from documents", value=True)

if st.button("Submit Query"):
    if user_query:
        with st.spinner("Fetching response..."):
            try:    
                # Get context and response
                relevant_chunks, response = process_query(system_message=SYSTEM_PROMPT, query=user_query, model=selected_model)
                
                # Extract context from results
                context = ""
                if show_context:
                    for c in relevant_chunks:
                        context += pages[c] 
                    st.subheader("Context Retrieved from Documents")
                    st.write(context)

                # Display response
                st.subheader("Response from the Chatbot")
                st.write(response)    
            except Exception as e:
                st.error(f"An error occurred: {e}")


# Adding response history
if "history" not in st.session_state:
    st.session_state.history = []

if st.button("Clear History"):
    st.session_state.history = []

# Save the query and response in history
if user_query and "response" in locals():
    st.session_state.history.append({"query": user_query, "response": response})

if st.session_state.history:
    st.subheader("Response History")
    for i, entry in enumerate(st.session_state.history, 1):
        st.markdown(f"**Query {i}:** {entry['query']}")
        st.markdown(f"**Response {i}:** {entry['response']}")
        st.markdown("---")

# Adding export option
if st.session_state.history:
    if st.button("Export History"):
        history_text = "\n\n".join([f"Query: {entry['query']}\nResponse: {entry['response']}" for entry in st.session_state.history])
        st.download_button("Download History", data=history_text, file_name="response_history.txt")
