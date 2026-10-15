"""Database layer for Milto AI"""
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = os.path.join(os.path.dirname(__file__), "milto.db")

SCHEMA = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL,
    answers_json TEXT NOT NULL,
    profile_json TEXT NOT NULL,
    analysis_json TEXT NOT NULL DEFAULT '{}',
    plan_json TEXT NOT NULL DEFAULT '[]',
    task_done_json TEXT NOT NULL DEFAULT '{}',
    activities_json TEXT NOT NULL DEFAULT '[]',
    activity_done_json TEXT NOT NULL DEFAULT '{}',
    activity_feedback_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS feedback (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    career_id TEXT NOT NULL,
    rating TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (user_id, career_id)
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_settings (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    theme TEXT NOT NULL DEFAULT 'dark',
    notifications_enabled INTEGER NOT NULL DEFAULT 0,
    reminder_time TEXT NOT NULL DEFAULT '18:00',
    motivation_style TEXT NOT NULL DEFAULT 'gentle',
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    day_key TEXT NOT NULL,
    self_awareness_json TEXT NOT NULL,
    plan_json TEXT NOT NULL,
    done_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    UNIQUE(user_id, day_key)
);

CREATE TABLE IF NOT EXISTS reflections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    day_key TEXT NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS career_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_type TEXT NOT NULL,
    current_career TEXT,
    target_career TEXT,
    plan_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_assessments_user_created ON assessments(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_user_id ON chat_messages(user_id, id);
CREATE INDEX IF NOT EXISTS idx_reflections_user_day ON reflections(user_id, day_key DESC);
CREATE INDEX IF NOT EXISTS idx_daily_user_day ON daily_items(user_id, day_key DESC);
"""


def now():
    return datetime.now(timezone.utc).isoformat()


def get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def _json(value, default):
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return default


def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


# ============ USERS ============
def create_user(username, password_hash):
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, password_hash, now()),
        )
        conn.execute(
            "INSERT OR IGNORE INTO user_settings (user_id, updated_at) VALUES (?, ?)",
            (cur.lastrowid, now()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_user_by_username(username):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_password(user_id, password_hash):
    conn = get_conn()
    conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))
    conn.commit()
    conn.close()


# ============ ASSESSMENTS ============
def save_assessment(user_id, answers, profile, plan, activities=None, analysis=None):
    conn = get_conn()
    cur = conn.execute(
        """INSERT INTO assessments 
           (user_id, created_at, answers_json, profile_json, analysis_json, plan_json, 
            task_done_json, activities_json, activity_done_json, activity_feedback_json) 
           VALUES (?, ?, ?, ?, ?, ?, '{}', ?, '{}', '{}')""",
        (user_id, now(), json.dumps(answers), json.dumps(profile),
         json.dumps(analysis or {}), json.dumps(plan), json.dumps(activities or [])),
    )
    conn.commit()
    aid = cur.lastrowid
    conn.close()
    return aid


def _decode_assessment(row):
    if not row:
        return None
    d = dict(row)
    d["answers"] = _json(d.pop("answers_json"), {})
    d["profile"] = _json(d.pop("profile_json"), {})
    d["analysis"] = _json(d.pop("analysis_json", "{}"), {})
    d["plan"] = _json(d.pop("plan_json"), [])
    d["task_done"] = _json(d.pop("task_done_json"), {})
    d["activities"] = _json(d.pop("activities_json"), [])
    d["activity_done"] = _json(d.pop("activity_done_json"), {})
    d["activity_feedback"] = _json(d.pop("activity_feedback_json"), {})
    return d


def get_latest_assessment(user_id):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM assessments WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,)
    ).fetchone()
    conn.close()
    return _decode_assessment(row)


def get_history(user_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, created_at, profile_json FROM assessments WHERE user_id = ? ORDER BY id ASC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [
        {"id": r["id"], "created_at": r["created_at"], "profile": _json(r["profile_json"], {})}
        for r in rows
    ]


def update_task_done(assessment_id, task_done):
    conn = get_conn()
    conn.execute("UPDATE assessments SET task_done_json = ? WHERE id = ?",
                 (json.dumps(task_done), assessment_id))
    conn.commit()
    conn.close()


def update_activity_done(assessment_id, activity_done):
    conn = get_conn()
    conn.execute("UPDATE assessments SET activity_done_json = ? WHERE id = ?",
                 (json.dumps(activity_done), assessment_id))
    conn.commit()
    conn.close()


def update_activities(assessment_id, activities):
    conn = get_conn()
    conn.execute("UPDATE assessments SET activities_json = ? WHERE id = ?",
                 (json.dumps(activities), assessment_id))
    conn.commit()
    conn.close()


def update_activity_feedback(assessment_id, feedback):
    conn = get_conn()
    conn.execute("UPDATE assessments SET activity_feedback_json = ? WHERE id = ?",
                 (json.dumps(feedback), assessment_id))
    conn.commit()
    conn.close()


# ============ FEEDBACK ============
def set_feedback(user_id, career_id, rating):
    conn = get_conn()
    if rating is None:
        conn.execute("DELETE FROM feedback WHERE user_id = ? AND career_id = ?",
                     (user_id, career_id))
    else:
        conn.execute(
            """INSERT INTO feedback (user_id, career_id, rating, updated_at) 
               VALUES (?, ?, ?, ?) 
               ON CONFLICT(user_id, career_id) DO UPDATE SET 
               rating = excluded.rating, updated_at = excluded.updated_at""",
            (user_id, career_id, rating, now()),
        )
    conn.commit()
    conn.close()


def get_feedback(user_id):
    conn = get_conn()
    rows = conn.execute("SELECT career_id, rating FROM feedback WHERE user_id = ?",
                        (user_id,)).fetchall()
    conn.close()
    return {row["career_id"]: row["rating"] for row in rows}


# ============ CHAT ============
def add_chat_message(user_id, role, content):
    conn = get_conn()
    conn.execute(
        "INSERT INTO chat_messages (user_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (user_id, role, content, now()),
    )
    conn.commit()
    conn.close()


def get_chat_history(user_id, limit=30):
    conn = get_conn()
    rows = conn.execute(
        "SELECT role, content FROM chat_messages WHERE user_id = ? ORDER BY id ASC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in rows]


# ============ SETTINGS ============
def get_settings(user_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,)).fetchone()
    if not row:
        conn.execute("INSERT OR IGNORE INTO user_settings (user_id, updated_at) VALUES (?, ?)",
                     (user_id, now()))
        conn.commit()
        row = conn.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    d = dict(row)
    d["notifications_enabled"] = bool(d["notifications_enabled"])
    return d


def update_settings(user_id, theme=None, notifications_enabled=None, reminder_time=None, motivation_style=None):
    current = get_settings(user_id)
    values = {
        "theme": theme if theme in ("dark", "light") else current["theme"],
        "notifications_enabled": int(bool(notifications_enabled)) if notifications_enabled is not None else int(current["notifications_enabled"]),
        "reminder_time": reminder_time or current["reminder_time"],
        "motivation_style": motivation_style if motivation_style in ("gentle", "direct", "celebrate") else current["motivation_style"],
    }
    conn = get_conn()
    conn.execute(
        """INSERT INTO user_settings (user_id, theme, notifications_enabled, reminder_time, motivation_style, updated_at)
           VALUES (?, ?, ?, ?, ?, ?)
           ON CONFLICT(user_id) DO UPDATE SET 
           theme=excluded.theme, 
           notifications_enabled=excluded.notifications_enabled,
           reminder_time=excluded.reminder_time, 
           motivation_style=excluded.motivation_style, 
           updated_at=excluded.updated_at""",
        (user_id, values["theme"], values["notifications_enabled"],
         values["reminder_time"], values["motivation_style"], now()),
    )
    conn.commit()
    conn.close()
    return get_settings(user_id)


# ============ DAILY ============
def get_daily(user_id, day_key):
    conn = get_conn()
    row = conn.execute("SELECT * FROM daily_items WHERE user_id = ? AND day_key = ?",
                       (user_id, day_key)).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row["id"], "day_key": row["day_key"],
        "self_awareness": _json(row["self_awareness_json"], {}),
        "plan": _json(row["plan_json"], []),
        "done": _json(row["done_json"], {}),
        "created_at": row["created_at"],
    }


def create_daily(user_id, day_key, self_awareness, plan):
    conn = get_conn()
    conn.execute(
        """INSERT OR IGNORE INTO daily_items 
           (user_id, day_key, self_awareness_json, plan_json, done_json, created_at) 
           VALUES (?, ?, ?, ?, '{}', ?)""",
        (user_id, day_key, json.dumps(self_awareness), json.dumps(plan), now()),
    )
    conn.commit()
    conn.close()
    return get_daily(user_id, day_key)


def update_daily_done(user_id, day_key, done):
    conn = get_conn()
    conn.execute("UPDATE daily_items SET done_json = ? WHERE user_id = ? AND day_key = ?",
                 (json.dumps(done), user_id, day_key))
    conn.commit()
    conn.close()
    return get_daily(user_id, day_key)


# ============ REFLECTIONS ============
def add_reflection(user_id, day_key, prompt, response):
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO reflections (user_id, day_key, prompt, response, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, day_key, prompt[:500], response[:2000], now()),
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def get_reflections(user_id, limit=30):
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, day_key, prompt, response, created_at FROM reflections WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============ CAREER PLANS ============
def save_career_plan(user_id, plan_type, current_career, target_career, plan_data):
    conn = get_conn()
    cur = conn.execute(
        """INSERT INTO career_plans (user_id, plan_type, current_career, target_career, plan_json, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, plan_type, current_career, target_career, json.dumps(plan_data), now()),
    )
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid


def get_career_plans(user_id, plan_type=None):
    conn = get_conn()
    if plan_type:
        rows = conn.execute(
            "SELECT * FROM career_plans WHERE user_id = ? AND plan_type = ? ORDER BY id DESC",
            (user_id, plan_type),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM career_plans WHERE user_id = ? ORDER BY id DESC", (user_id,)
        ).fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "plan_type": r["plan_type"],
            "current_career": r["current_career"],
            "target_career": r["target_career"],
            "plan": _json(r["plan_json"], {}),
            "created_at": r["created_at"],
        }
        for r in rows
    ]