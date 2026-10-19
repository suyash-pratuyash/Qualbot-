import os

BOOKING_URL = os.getenv(
    "CALENDLY_URL",
    "https://calendly.com/your-team/qualbot-demo",
)


def get_booking_action(tier: str) -> dict[str, str] | None:
    """Return a booking action for a hot lead."""
    if tier != "hot":
        return None
    return {"type": "book_meeting", "url": BOOKING_URL}


def route_lead(tier: str, session_id: str) -> dict[str, str] | None:
    """Create a meeting action and print an alert for hot leads."""
    action = get_booking_action(tier)
    if action is None:
        return None

    print(f"[sales alert] Hot lead is ready for follow-up: session_id={session_id}")
    return action
