from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.llms import Ollama

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import os
import shutil

# ---------------------------------
# FastAPI App
# ---------------------------------
app = FastAPI()

# ---------------------------------
# Enable CORS
# ---------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------
# Create uploads folder if missing
# ---------------------------------
os.makedirs("uploads", exist_ok=True)

# ---------------------------------
# Load Embedding Model
# ---------------------------------
print("Loading embeddings...")

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

# ---------------------------------
# Load Vector Database
# ---------------------------------
print("Loading vector database...")

vector_db = FAISS.load_local(
    "vector_store",
    embeddings,
    allow_dangerous_deserialization=True
)

# ---------------------------------
# Better Retriever
# ---------------------------------
retriever = vector_db.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 10
    }
)

# ---------------------------------
# Load Local AI Model (OLLAMA)
# ---------------------------------
print("Loading Ollama model...")

llm = Ollama(
    model="llama3"
)

print("Backend ready!")

# ---------------------------------
# Request Schema
# ---------------------------------
class QueryRequest(BaseModel):
    question: str

# ---------------------------------
# Ask Endpoint
# ---------------------------------
@app.post("/ask")
def ask_question(request: QueryRequest):

    query = request.question

    # Retrieve relevant documents
    docs = retriever.invoke(query)

    # Build context
    context = "\n\n".join([
        doc.page_content for doc in docs
    ])

    # Simple effective prompt
    prompt = f"""
Use the context below to answer the question.

If the answer is not in the context,
answer normally like a helpful AI assistant.

Context:
{context}

Question:
{query}

Answer:
"""

    # Generate response
    answer = llm.invoke(prompt)

    # Sources
    sources = list(set([
        doc.metadata.get("source", "unknown")
        for doc in docs
    ]))

    return {
        "answer": answer,
        "sources": sources
    }

# ---------------------------------
# Upload Endpoint
# ---------------------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    # Save uploaded file
    file_path = os.path.join(
        "uploads",
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Load PDF
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    # Clean + metadata
    for doc in docs:

        doc.page_content = doc.page_content.replace(
            "\n",
            " "
        )

        doc.page_content = " ".join(
            doc.page_content.split()
        )

        doc.metadata["source"] = file.filename
        doc.metadata["folder"] = "uploads"

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_documents(docs)

    # Add to existing vector DB
    vector_db.add_documents(chunks)

    # Save updated DB
    vector_db.save_local("vector_store")

    return {
        "message": f"{file.filename} uploaded successfully!"
    }