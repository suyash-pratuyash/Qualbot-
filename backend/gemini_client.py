import time
from typing import Literal
from pathlib import Path

from google import genai
from google.genai import errors
from dotenv import load_dotenv
from pydantic import BaseModel

# Local development settings from backend/.env take precedence over saved shell
# variables; the file is excluded from Git.
load_dotenv(Path(__file__).with_name(".env"), override=True)

client: genai.Client | None = None


def _get_client() -> genai.Client:
    global client
    if client is None:
        try:
            client = genai.Client()  # reads GEMINI_API_KEY from the environment
        except Exception as e:
            print(f"[Gemini] client initialization failed: {e}")
            raise RuntimeError("Gemini client initialization failed") from e
    return client


# Tried in order. Verify each name is available to your API key.
MODELS = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash","gemma-4-31b-it"]

# Temporary errors worth retrying (rate limit / server overloaded or busy)
RETRY_CODES = (429, 500, 503, 504)


# ---------- Shared helper: retry + model fallback ----------

def _generate(contents: str, config=None):
    """Try each model in order; if all fail, wait briefly and do one more round."""
    api_client = _get_client()
    for round_no in range(2):          # 2 full rounds over all models
        for name in MODELS:
            try:
                kwargs = {"model": name, "contents": contents}
                if config is not None:
                    kwargs["config"] = config
                return api_client.models.generate_content(**kwargs)
            except errors.APIError as e:
                print(f"[{name}] round {round_no + 1} failed: {e.code}")
            except Exception as e:
                print(f"[{name}] failed: {e}")
            # falls through to the next model immediately
        if round_no == 0:
            time.sleep(2)              # pause only after every model failed
    raise RuntimeError("All Gemini models failed")

# ---------- Phase 1: plain chat ----------

def ask_gemini(prompt: str) -> str:
    return _generate(prompt).text


# ---------- Phase 2: BANT extraction ----------

class BANT(BaseModel):
    budget: Literal["unknown", "none", "limited", "confirmed"]
    authority: Literal["unknown", "influencer", "decision_maker"]
    need: Literal["unknown", "vague", "clear"]
    timeline: Literal["unknown", "long_term", "soon", "immediate"]


EXTRACTION_PROMPT = """You extract sales qualification data from a website visitor's message.
Use ONLY what the visitor actually said. If something is not mentioned, use "unknown". Never guess.

budget: "none" = says they have no budget; "limited" = says budget is tight or small;
        "confirmed" = states an amount or says budget is approved.
authority: "decision_maker" = owner, founder, director, or says they decide;
        "influencer" = researching for someone else or needs approval.
need: "clear" = describes a specific problem; "vague" = just browsing or curious.
timeline: "immediate" = within about 2 weeks; "soon" = within about 3 months;
        "long_term" = later than that or no rush.
"""


def extract_bant(message: str) -> BANT:
    response = _generate(
        EXTRACTION_PROMPT + "\nVisitor message: " + message,
        config={
            "response_mime_type": "application/json",
            "response_schema": BANT,
        },
    )
    if response.parsed is None:
        raise RuntimeError("BANT extraction returned unparseable output")
    return response.parsed