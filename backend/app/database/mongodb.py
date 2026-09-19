"""Central MongoDB connection + persistence helpers. Owned by Safa.

Keep ALL database calls here. Do not scatter pymongo calls into agents/routes.
"""

import os
from datetime import datetime

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

_client: MongoClient | None = None
_db: Database | None = None


def get_db() -> Database:
    """Lazily create and return the MongoDB database handle."""
    global _client, _db
    if _db is None:
        uri = os.getenv("MONGODB_URI")
        if not uri:
            raise RuntimeError("MONGODB_URI is not set in the environment (.env)")
        _client = MongoClient(uri)
        _db = _client.get_database("contractlens")
    return _db


def contracts_col() -> Collection:
    return get_db()["contracts"]


def obligations_col() -> Collection:
    return get_db()["obligations"]


def alerts_col() -> Collection:
    return get_db()["alerts"]


def comparisons_col() -> Collection:
    return get_db()["comparisons"]


# ---- Contract persistence -------------------------------------------------

def save_contract(contract_doc: dict) -> str:
    contract_doc["created_at"] = contract_doc.get("created_at", datetime.utcnow())
    contract_doc["updated_at"] = datetime.utcnow()
    contracts_col().update_one(
        {"contract_id": contract_doc["contract_id"]},
        {"$set": contract_doc},
        upsert=True,
    )
    return contract_doc["contract_id"]


def get_contract_by_id(contract_id: str) -> dict | None:
    return contracts_col().find_one({"contract_id": contract_id}, {"_id": 0})


def list_contracts() -> list[dict]:
    return list(contracts_col().find({}, {"_id": 0}))


# ---- Obligation persistence ------------------------------------------------

def save_obligations(contract_id: str, obligations: list[dict]) -> None:
    if not obligations:
        return
    obligations_col().delete_many({"contract_id": contract_id})
    obligations_col().insert_many(obligations)


def get_obligations_for_contract(contract_id: str) -> list[dict]:
    return list(obligations_col().find({"contract_id": contract_id}, {"_id": 0}))


def get_all_obligations() -> list[dict]:
    return list(obligations_col().find({}, {"_id": 0}))


# ---- Comparisons ------------------------------------------------------------

def save_comparison(comparison_doc: dict) -> None:
    comparison_doc["created_at"] = datetime.utcnow()
    comparisons_col().insert_one(comparison_doc)
