"""Agent 5: ContractLens Orchestrator. Owned by Safa.

Routes requests to the right agent(s). Stays simple - no autonomous planning.
"""

from app.database.mongodb import get_contract_by_id
from app.services.gemini_service import generate_response
from app.services.rag_service import retrieve_relevant_chunks
from app.utils.prompts import QA_PROMPT


def route_request(request_type: str, payload: dict) -> dict:
    """Generic entry point other modules can call instead of hard-wiring flows.

    request_type examples: "qa", "review_summary".
    Most routes call the relevant service/agent directly (see Section 8.5 flows);
    this function exists for cases where a single call needs to fan out.
    """
    if request_type == "qa":
        return answer_question(payload["contract_id"], payload["question"])
    raise ValueError(f"Unknown request_type: {request_type}")


def answer_question(contract_id: str, question: str) -> dict:
    """Orchestrator -> RAG retrieval -> Gemini -> answer with sources.

    Used by routes/chat.py.
    """
    contract = get_contract_by_id(contract_id)
    if contract is None:
        return {"answer": "Contract not found.", "sources": []}

    chunks = retrieve_relevant_chunks(contract_id, question, top_k=5)
    if not chunks:
        return {
            "answer": "The system could not find sufficient evidence in this contract to answer that question.",
            "sources": [],
        }

    evidence_text = "\n\n".join(f"[Page {c['page']}] {c['text']}" for c in chunks)
    prompt = QA_PROMPT.format(question=question, evidence_chunks=evidence_text)

    try:
        answer = generate_response(prompt)
    except RuntimeError as exc:
        return {"answer": f"The AI service is currently unavailable: {exc}", "sources": []}

    sources = [{"page": c["page"], "section": c.get("section"), "text": c["text"][:300]} for c in chunks]
    return {"answer": answer, "sources": sources}
