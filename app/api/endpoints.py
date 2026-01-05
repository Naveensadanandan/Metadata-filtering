from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.engine.generator import generate_sql_and_execute
from typing import Optional

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    status: Optional[str]
    error_type: Optional[str]
    message: Optional[str]
    retrieved_items: list[dict]
    retrieved_columns: list[dict]

@app.post("/query", response_model=QueryResponse)
async def query_database(request: QueryRequest):
    try:
        result = generate_sql_and_execute(request.question)
        return result
    except Exception as e:
        # In production, log this error to Sentry/Datadog
        raise HTTPException(status_code=500, detail=str(e))