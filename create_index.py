"""Build the knowledge index using the workflow's embedding model."""
import hashlib
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from src.config import PROJECT_ROOT, EMBEDDING_MODEL, VECTORSTORE_DIR, KNOWLEDGE_FILE


def main():
    print(f"Loading and chunking {KNOWLEDGE_FILE.name}...")
    docs = TextLoader(str(KNOWLEDGE_FILE), encoding="utf-8").load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50).split_documents(docs)
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = Chroma(persist_directory=VECTORSTORE_DIR, embedding_function=embeddings)
    ids = [hashlib.sha256(f"{i}:{chunk.page_content}".encode()).hexdigest() for i, chunk in enumerate(chunks)]
    print(f"Embedding {len(chunks)} chunks with {EMBEDDING_MODEL}...")
    vectorstore.add_documents(chunks, ids=ids)
    old_ids = set(vectorstore.get()["ids"]) - set(ids)
    if old_ids:
        vectorstore.delete(ids=list(old_ids))
    matches = vectorstore.similarity_search("What are your pricing options?", k=3)
    print(f"Index ready. Retrieval test returned {len(matches)} documents.")


if __name__ == "__main__":
    main()
