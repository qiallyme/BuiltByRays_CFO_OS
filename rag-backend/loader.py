import os
import hashlib

def load_documents(folder):
    """Load documents from the specified folder"""
    docs = []
    
    if not os.path.exists(folder):
        print(f"⚠️  Warning: Vault folder not found at {folder}")
        return docs
    
    try:
        for root, _, files in os.walk(folder):
            for f in files:
                # Support markdown, text, and other common document formats
                if f.endswith(('.md', '.txt', '.rst', '.adoc')):
                    file_path = os.path.join(root, f)
                    try:
                        with open(file_path, encoding='utf-8') as file:
                            text = file.read()
                            # Generate a unique ID for the document
                            doc_id = hashlib.sha256((f + text).encode()).hexdigest()
                            docs.append({
                                "text": text,
                                "source": file_path,
                                "id": doc_id
                            })
                    except UnicodeDecodeError:
                        print(f"⚠️  Warning: Could not read {file_path} (encoding issue)")
                        continue
                    except Exception as e:
                        print(f"⚠️  Warning: Could not read {file_path}: {e}")
                        continue
        
        print(f"📁 Loaded {len(docs)} documents from {folder}")
        return docs
    except Exception as e:
        print(f"❌ Error loading documents from {folder}: {e}")
        return docs