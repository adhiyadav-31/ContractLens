"""Contract Q&A endpoint. Owned by Safa."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.orchestrator import answer_question
from app.database.mongodb import get_contract_by_id

router = APIRouter(prefix="/contracts", tags=["chat"])


class ChatRequest(BaseModel):
    question: str


@router.post("/{contract_id}/chat")
def chat_with_contract(contract_id: str, request: ChatRequest):
    if get_contract_by_id(contract_id) is None:
        raise HTTPException(status_code=404, detail="Contract not found.")
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    return answer_question(contract_id, request.question)
