from fastapi import FastAPI
from pydantic import BaseModel
from embedder import query_vector_store

app = FastAPI()

class ChatQuery(BaseModel):
    question: str

@app.post("/chat")
def chat(query: ChatQuery):
    response = query_vector_store(query.question)
    return {"response": response}
