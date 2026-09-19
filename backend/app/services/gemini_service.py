"""Central Gemini API wrapper. Owned by Safa.

Every agent calls through here. Never initialize the Gemini client anywhere else.
"""

import json
import os

from google import genai

_client: genai.Client | None = None

DEFAULT_MODEL = "gemini-2.0-flash"


def get_gemini_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in the environment (.env)")
        _client = genai.Client(api_key=api_key)
    return _client


def generate_response(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Plain text generation. Raises RuntimeError on API failure (caller should
    catch and translate into a clean HTTP error — see error handling rules)."""
    client = get_gemini_client()
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        return response.text or ""
    except Exception as exc:  # noqa: BLE001 - deliberately broad, translated at route level
        raise RuntimeError(f"Gemini API request failed: {exc}") from exc


def generate_structured_output(prompt: str, model: str = DEFAULT_MODEL) -> dict | list:
    """Generate JSON output and parse it. Strips markdown code fences if present.

    Raises RuntimeError if the model does not return valid JSON — callers should
    treat this as a low-confidence extraction and flag for review rather than crash.
    """
    raw = generate_response(prompt, model=model)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Gemini did not return valid JSON: {exc}\nRaw: {raw[:500]}") from exc
