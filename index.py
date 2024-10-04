import streamlit as st
import requests
 
upload_url = "http://localhost:8000/upload"
query_url = "http://localhost:8000/query"
 
def upload_pdf(pdf_file):
    files = {'pdf': pdf_file}
    response = requests.post(upload_url, files=files)
    return response.json()
 
def send_query(question):
    data = {'question': question}
    response = requests.post(query_url, data=data)
    return response.json() if response.status_code == 200 else {"error": "Something went wrong"}
 
st.title("PDF Chatbot")
 
uploaded_pdf = st.file_uploader("Upload a PDF file", type="pdf")
 
if uploaded_pdf:
    if st.button("Upload PDF"):
        with st.spinner("Uploading PDF..."):
            result = upload_pdf(uploaded_pdf)
        if "error" in result:
            st.error(result["error"])
        else:
            st.success(result["message"])
 
question = st.text_input("Enter your question")
 
if question:
    if st.button("Ask Question"):
        with st.spinner("Sending query..."):
            result = send_query(question)
        
        if "error" in result:
            st.error(result["error"])
        else:
            st.success(result["answer"])