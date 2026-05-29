"""
SQLite database for run history, logs, and generated file persistence.
"""
from __future__ import annotations

import asyncio
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).parent / "agent_factory.db"

_DDL = [
    """
    CREATE TABLE IF NOT EXISTS runs (
        id             TEXT PRIMARY KEY,
        requirement    TEXT NOT NULL,
        status         TEXT NOT NULL DEFAULT 'running',
        project_name   TEXT,
        output_path    TEXT,
        test_passed    INTEGER DEFAULT 0,
        token_usage    TEXT,
        error_log      TEXT,
        created_at     TEXT NOT NULL,
        completed_at   TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS run_logs (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id      TEXT    NOT NULL,
        agent       TEXT    NOT NULL,
        level       TEXT    NOT NULL DEFAULT 'info',
        message     TEXT    NOT NULL,
        timestamp   TEXT    NOT NULL,
        FOREIGN KEY (run_id) REFERENCES runs(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS run_files (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id      TEXT    NOT NULL,
        filename    TEXT    NOT NULL,
        content     TEXT    NOT NULL,
        FOREIGN KEY (run_id) REFERENCES runs(id)
    )
    """,
]


# ── init ──────────────────────────────────────────────────────────────────────

async def init_db() -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _init_sync)


def _init_sync() -> None:
    conn = _conn()
    try:
        for ddl in _DDL:
            conn.execute(ddl)
        conn.commit()
    finally:
        conn.close()


# ── helpers ───────────────────────────────────────────────────────────────────

def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


# ── write helpers ─────────────────────────────────────────────────────────────

def save_run(run_id: str, requirement: str) -> None:
    with _conn() as c:
        c.execute(
            "INSERT INTO runs (id, requirement, status, created_at) VALUES (?, ?, 'running', ?)",
            (run_id, requirement, datetime.utcnow().isoformat()),
        )
        c.commit()


def update_run(run_id: str, **kwargs: Any) -> None:
    if not kwargs:
        return
    fields = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [run_id]
    with _conn() as c:
        c.execute(f"UPDATE runs SET {fields} WHERE id = ?", values)
        c.commit()


def save_log(run_id: str, agent: str, level: str, message: str) -> None:
    with _conn() as c:
        c.execute(
            "INSERT INTO run_logs (run_id, agent, level, message, timestamp) VALUES (?, ?, ?, ?, ?)",
            (run_id, agent, level, message, datetime.utcnow().isoformat()),
        )
        c.commit()


def save_files(run_id: str, files: dict[str, str]) -> None:
    if not files:
        return
    rows = [(run_id, fname, content) for fname, content in files.items()]
    with _conn() as c:
        c.executemany(
            "INSERT OR REPLACE INTO run_files (run_id, filename, content) VALUES (?, ?, ?)",
            rows,
        )
        c.commit()


# ── read helpers ──────────────────────────────────────────────────────────────

def get_runs(limit: int = 20) -> list[dict]:
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM runs ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_run(run_id: str) -> dict | None:
    with _conn() as c:
        row = c.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        if not row:
            return None
        result = dict(row)
        file_rows = c.execute(
            "SELECT filename, content FROM run_files WHERE run_id = ?", (run_id,)
        ).fetchall()
        result["files"] = {r["filename"]: r["content"] for r in file_rows}
        log_rows = c.execute(
            "SELECT agent, level, message, timestamp FROM run_logs WHERE run_id = ? ORDER BY id",
            (run_id,),
        ).fetchall()
        result["logs"] = [dict(r) for r in log_rows]
    return result
