import sqlite3
import uuid
from pathlib import Path
from datetime import datetime, timezone
from contextlib import contextmanager
 
BACKEND_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("DB_PATH", str(BACKEND_DIR / "chat_history.db")))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
 
 
def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
 
 
def _new_id() -> str:
    return uuid.uuid4().hex
 
 
@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
 
 
def init_db() -> None:
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id          TEXT PRIMARY KEY,
                title       TEXT,
                created_at  TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id          TEXT PRIMARY KEY,
                session_id  TEXT NOT NULL REFERENCES sessions(id),
                parent_id   TEXT REFERENCES messages(id),
                role        TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content     TEXT NOT NULL,
                created_at  TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_session
            ON messages(session_id)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_parent
            ON messages(parent_id)
        """)
 
 
# ---------------------------------------------------------------- sessions
 
def create_session(title: str, s_id: str = None) -> str:
    if s_id is None:
        s_id = str(uuid.uuid4())
    session_id = s_id
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO sessions (id, title, created_at) VALUES (?, ?, ?)",
            (session_id, title, _now()),
        )
    return session_id
 
 
def session_exists(session_id: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
    return row is not None
 
 
def message_exists(message_id: str | None) -> bool:
    if message_id is None:
        return False
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM messages WHERE id = ?", (message_id,)
        ).fetchone()
    return row is not None
 
 
def latest_leaf(session_id: str) -> str | None:
    with get_conn() as conn:
        row = conn.execute(
            """SELECT id FROM messages
               WHERE session_id = ?
               ORDER BY created_at DESC LIMIT 1""",
            (session_id,),
        ).fetchone()
    return row["id"] if row else None
 
 
# ---------------------------------------------------------------- messages
 
def add_message(session_id: str, role: str, content: str, parent_id: str | None) -> str:
    msg_id = _new_id()
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO messages (id, session_id, parent_id, role, content, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (msg_id, session_id, parent_id, role, content, _now()),
        )
    return msg_id
 
 
def get_branch(leaf_id: str) -> list[dict]:
    if leaf_id is None:
        return []
    with get_conn() as conn:
        chain: list[dict] = []
        current_id = leaf_id
        while current_id is not None:
            row = conn.execute(
                "SELECT id, parent_id, role, content, created_at FROM messages WHERE id = ?",
                (current_id,),
            ).fetchone()
            if row is None:
                break
            chain.append(dict(row))
            current_id = row["parent_id"]
    chain.reverse()
    return chain
