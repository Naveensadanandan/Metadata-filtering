from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.engine.generator import generate_sql_and_execute

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    generated_sql: str

@router.post("/query", response_model=QueryResponse)
async def query_database(request: QueryRequest):
    try:
        result = generate_sql_and_execute(request.question)
        return result
    except Exception as e:
        # In production, log this error to Sentry/Datadog
        raise HTTPException(status_code=500, detail=str(e))