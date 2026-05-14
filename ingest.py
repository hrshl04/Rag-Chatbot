from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

import os

print("Starting ingestion process...")

# ---------------------------------
# Folders to ingest from
# ---------------------------------
folders = ["data", "uploads"]

documents = []

# ---------------------------------
# Load PDFs
# ---------------------------------
print("Loading documents...")

for folder in folders:

    # Skip if folder doesn't exist
    if not os.path.exists(folder):
        continue

    for file in os.listdir(folder):

        if file.endswith(".pdf"):

            file_path = os.path.join(folder, file)

            print(f"Loading {file}...")

            loader = PyPDFLoader(file_path)
            docs = loader.load()

            for doc in docs:

                # Clean text
                doc.page_content = doc.page_content.replace("\n", " ")
                doc.page_content = " ".join(
                    doc.page_content.split()
                )

                # Metadata
                doc.metadata["source"] = file
                doc.metadata["folder"] = folder
                doc.metadata["page"] = doc.metadata.get("page", 0)

            documents.extend(docs)

print(f"Total documents loaded: {len(documents)}")

# ---------------------------------
# Split Documents
# ---------------------------------
print("Splitting documents...")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = text_splitter.split_documents(documents)

print(f"Total chunks created: {len(chunks)}")

# ---------------------------------
# Load Embedding Model
# ---------------------------------
print("Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5",
    model_kwargs={"device": "cpu"},  # change to cuda if GPU available
    encode_kwargs={"normalize_embeddings": True}
)

# ---------------------------------
# Create Vector Database
# ---------------------------------
print("Creating vector database...")

vector_db = FAISS.from_documents(
    chunks,
    embeddings
)

# Save vector DB
vector_db.save_local("vector_store")

print("Vector database created successfully!")