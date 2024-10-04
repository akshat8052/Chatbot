from fastapi import FastAPI, UploadFile, File, Form
from langchain import hub
from langchain.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
# from langchain_core.messages import HumanMessage, AIMessage
import os

app = FastAPI()

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = ""

llm = ChatOpenAI(model="gpt-4")

vector_store = None
# print(llm.invoke([HumanMessage(content="Hi! I'm Bob")]))
# print(llm.invoke([HumanMessage(content="What's my name?")]))

@app.on_event("startup")
async def startup_event():
    global vector_store
    vector_store = None  # Clear the vector store at startup

    

def process_pdf(pdf_file_path: str):
    loader = PyPDFLoader(pdf_file_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)

    global vector_store
    vector_store = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
    # vector_store.persist()  

@app.post("/upload")
async def upload_pdf(pdf: UploadFile = File(...)):
    try:
        pdf_path = f"./temp/{pdf.filename}"
        with open(pdf_path, "wb") as f:
            f.write(await pdf.read())

        process_pdf(pdf_path)

        return {"message": "PDF processed and embeddings stored."}

    except Exception as e:
        return {"error": str(e)}

    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

@app.post("/query")
async def query(question: str = Form(...)):
    try:
        if vector_store is None:
            return {"error": "No PDF has been uploaded yet."}

        retriever = vector_store.as_retriever()

        prompt = hub.pull("rlm/rag-prompt")

        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        answer = rag_chain.invoke(question)


        return {"answer": answer}

    except Exception as e:
        return {"error": str(e)}

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


