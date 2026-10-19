import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

DB_PATH = Path(__file__).with_name("qualbot.db")


@contextmanager
def _connection() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db() -> None:
    """Create the lead and message tables if they do not exist."""
    with _connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                session_id TEXT PRIMARY KEY,
                bant TEXT NOT NULL,
                score INTEGER NOT NULL,
                tier TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                ts TEXT NOT NULL
            )
            """
        )


def save_message(session_id: str, role: str, content: str) -> int:
    """Store one conversation message and return its row ID."""
    with _connection() as connection:
        cursor = connection.execute(
            "INSERT INTO messages (session_id, role, content, ts) VALUES (?, ?, ?, ?)",
            (session_id, role, content, _now()),
        )
        return int(cursor.lastrowid)


def upsert_lead(
    session_id: str,
    bant: dict[str, Any],
    score: int,
    tier: str,
) -> None:
    """Insert a lead or update its qualification data without changing created_at."""
    now = _now()
    with _connection() as connection:
        connection.execute(
            """
            INSERT INTO leads (session_id, bant, score, tier, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                bant = excluded.bant,
                score = excluded.score,
                tier = excluded.tier,
                updated_at = excluded.updated_at
            """,
            (session_id, json.dumps(bant), score, tier, now, now),
        )


def get_lead(session_id: str) -> dict[str, Any] | None:
    """Return one lead with BANT decoded from JSON, or None if it does not exist."""
    with _connection() as connection:
        row = connection.execute(
            "SELECT session_id, bant, score, tier, created_at, updated_at "
            "FROM leads WHERE session_id = ?",
            (session_id,),
        ).fetchone()
    if row is None:
        return None
    lead = dict(row)
    lead["bant"] = json.loads(lead["bant"])
    return lead


def list_leads(limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    """Return a page of leads, newest updates first, with decoded BANT data."""
    with _connection() as connection:
        rows = connection.execute(
            """
            SELECT session_id, bant, score, tier, created_at, updated_at
            FROM leads
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
    leads = [dict(row) for row in rows]
    for lead in leads:
        lead["bant"] = json.loads(lead["bant"])
    return leads


def get_messages(session_id: str) -> list[dict[str, Any]]:
    """Return a session's messages in insertion order."""
    with _connection() as connection:
        rows = connection.execute(
            """
            SELECT id, session_id, role, content, ts
            FROM messages
            WHERE session_id = ?
            ORDER BY id
            """,
            (session_id,),
        ).fetchall()
    return [dict(row) for row in rows]
