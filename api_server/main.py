from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import os
import uuid

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

class Question(BaseModel):
    text: str

@app.post("/ask")
def ask_question(q: Question):
    if not q.text.strip():
        raise HTTPException(status_code=400, detail="Empty question")

    question_id = str(uuid.uuid4())
    r.rpush("questions", f"{question_id}|{q.text}")
    return {"question_id": question_id, "status": "queued"}

@app.get("/answer/{question_id}")
def get_answer(question_id: str):
    answer = r.get(f"answer:{question_id}")
    if not answer:
        return {"status": "pending"}
    return {"status": "done", "answer": answer}
