# backend/scoring.py
WEIGHTS = {"need": 30, "budget": 25, "timeline": 25, "authority": 20}
EMPTY = (None, "", "unknown", "none", "null", "not provided", "n/a")
POINTS = {
    "budget": {"confirmed": 1.0, "limited": 0.6, "none": 0.0},
    "authority": {"decision_maker": 1.0, "influencer": 0.6},
    "need": {"clear": 1.0, "vague": 0.6},
    "timeline": {"immediate": 1.0, "soon": 0.6, "long_term": 0.3},
}


def _has(v) -> bool:
    return v is not None and str(v).strip().lower() not in EMPTY


def merge_bant(old: dict, new: dict) -> dict:
    """Keep earlier answers; overwrite only when the new turn gives a real value."""
    merged = dict(old or {})
    for key in WEIGHTS:
        value = (new or {}).get(key)
        # "none" is a meaningful answer for budget (no available budget).
        if _has(value) or (key == "budget" and str(value).strip().lower() == "none"):
            merged[key] = new[key]
    return merged


def score_lead(bant: dict) -> dict:
    """Return score (0-100), tier and a per-field breakdown."""
    breakdown = {}
    for key, weight in WEIGHTS.items():
        val = str(bant.get(key, "") or "")
        if not _has(val):
            breakdown[key] = 0
            continue
        # These values are the categories emitted by gemini_client.BANT. Keep
        # scoring in sync with that schema rather than inspecting prose.
        breakdown[key] = round(weight * POINTS.get(key, {}).get(val.lower(), 0))

    score = sum(breakdown.values())
    tier = "hot" if score >= 70 else "warm" if score >= 40 else "cold"
    return {"score": score, "tier": tier, "breakdown": breakdown}
