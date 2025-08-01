import os
import openai
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
import hashlib
from loader import load_documents
import chromadb

client = chromadb.Client()
collection = client.get_or_create_collection(name="client_vault")

def embed_documents(vault_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "../vault"))):
    """Embed documents from the vault into the vector store"""
    try:
        # Clear existing documents
        collection.delete(where={})
        
        docs = load_documents(vault_path)
        print(f"📚 Loading {len(docs)} documents from vault...")
        
        for i, doc in enumerate(docs):
            try:
                collection.add(
                    documents=[doc['text']],
                    metadatas=[{"source": doc['source']}],
                    ids=[f"doc_{i}"]
                )
            except Exception as e:
                print(f"⚠️  Warning: Could not embed document {doc['source']}: {e}")
                continue
        
        print(f"✅ Successfully embedded {len(docs)} documents")
        return True
    except Exception as e:
        print(f"❌ Error embedding documents: {e}")
        return False

def query_vector_store(query, n_results=3):
    """Query the vector store for relevant documents"""
    try:
        results = collection.query(query_texts=[query], n_results=n_results)
        if results and "documents" in results and results["documents"]:
            return results["documents"][0]  # Return the first query's results
        return []
    except Exception as e:
        print(f"❌ Error querying vector store: {e}")
        return []
