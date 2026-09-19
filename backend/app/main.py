"""FastAPI application entry point. Owned by Safa.

No AI logic here - only app wiring: CORS, routers, health check.
"""

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.routes import alerts, chat, compare, contracts, due_diligence, obligations  # noqa: E402

app = FastAPI(title="ContractLens API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten before any real deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contracts.router)
app.include_router(obligations.router)
app.include_router(chat.router)
app.include_router(compare.router)
app.include_router(due_diligence.router)
app.include_router(alerts.router)


@app.get("/health")
def health():
    return {"status": "ok"}
