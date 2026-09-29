import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from src.pipeline import execute_plan_with_retry

app = FastAPI(
    title="E-Commerce Knowledge Graph API",
    description="API for querying the e-commerce knowledge graph using natural language.",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    success: bool
    answer: str
    rows: List[Dict[str, Any]]

from src.logger import get_logger

api_logger = get_logger("kg_api")

@app.post("/query", response_model=QueryResponse)
def query_graph(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
    api_logger.info("[API] POST /query received | Question: \"%s\"", request.question)
    try:
        result = execute_plan_with_retry(request.question)
        answer = result.get("answer", "")
        # Mark as unsuccessful if it resulted in a graceful failure
        is_success = not answer.startswith("Graceful failure:")
        api_logger.info("[API] Request complete | Success: %s | Records returned: %d", is_success, len(result.get("rows", [])))
        return QueryResponse(
            success=is_success,
            answer=answer,
            rows=result.get("rows", [])
        )

    except Exception as e:

        api_logger.error("Unhandled API Exception: %s", str(e))
        return QueryResponse(
            success=False,
            answer=f"Server error: {str(e)}",
            rows=[]
        )
        
@app.get("/")
def health_check():
    return {"status": "ok", "message": "Knowledge Graph API is running. Visit /docs for Swagger UI."}
