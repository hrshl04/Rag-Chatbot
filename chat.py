from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Loading vector database...")

# Embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5",
    model_kwargs={"device": "cpu"},   # change to "cuda" if using GPU
    encode_kwargs={"normalize_embeddings": True}
)

# Load FAISS database
vector_db = FAISS.load_local(
    "vector_store",
    embeddings,
    allow_dangerous_deserialization=True
)

# Better retriever
retriever = vector_db.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 10
    }
)

# OpenAI model
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

print("\n💬 Chat system ready! Type 'exit' to quit.\n")

# Chat memory
chat_history = []

while True:

    query = input("🧑 You: ")

    if query.lower() in ["exit", "quit"]:
        print("👋 Goodbye!")
        break

    # Retrieve relevant documents
    docs = retriever.invoke(query)

    # Build context
    context = "\n\n".join([
        doc.page_content for doc in docs
    ])

    # Previous conversation memory
    history = "\n".join(chat_history[-4:])

    # Simple and effective prompt
    prompt = f"""
Use the context below to answer the question.
If the answer is not in the context, say you don't know.

Previous Conversation:
{history}

Context:
{context}

Question:
{query}

Answer:
"""

    # Generate response
    response = llm.invoke(prompt)

    answer = response.content.strip()

    # Save chat memory
    chat_history.append(f"User: {query}")
    chat_history.append(f"Assistant: {answer}")

    # Print answer
    print("\n🤖 AI Answer:\n")
    print(answer)

    # Show sources
    sources = list(set([
        doc.metadata.get("source", "unknown")
        for doc in docs
    ]))

    print("\n📚 Sources:")
    for src in sources:
        print(f"- {src}")

    print("\n" + "-" * 50 + "\n")