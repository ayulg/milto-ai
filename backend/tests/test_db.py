import pytest
import sqlite3
import db


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    test_db = tmp_path / "test_milto.db"
    monkeypatch.setattr(db, "DB_PATH", str(test_db))
    db.init_db()
    return db


def test_chat_history_returns_latest_messages_in_order(isolated_db):
    user_id = isolated_db.create_user("chat@test.local", "test_hash")

    for i in range(35):
        isolated_db.add_chat_message(user_id, "user", f"Message {i + 1}")

    history = isolated_db.get_chat_history(user_id, limit=30)

    expected = [f"Message {i}" for i in range(6, 36)]
    actual = [message["content"] for message in history]

    assert actual == expected


def test_negative_chat_history_limit_does_not_return_all(isolated_db):
    user_id = isolated_db.create_user("chatlimit@test.local", "test_hash")

    for i in range(5):
        isolated_db.add_chat_message(user_id, "user", f"Message {i}")

    history = isolated_db.get_chat_history(user_id, limit=-1)

    assert history == []


def test_negative_reflection_limit_does_not_return_all(isolated_db):
    user_id = isolated_db.create_user("reflection@test.local", "test_hash")

    for i in range(5):
        isolated_db.add_reflection(
            user_id, "2026-10-31", f"Prompt {i}", f"Response {i}"
        )

    reflections = isolated_db.get_reflections(user_id, limit=-1)

    assert reflections == []


def test_users_cannot_read_each_others_feedback(isolated_db):
    user_a = isolated_db.create_user("usera@test.local", "hash_a")
    user_b = isolated_db.create_user("userb@test.local", "hash_b")

    isolated_db.set_feedback(user_a, "software-engineer", "interested")
    isolated_db.set_feedback(user_b, "teacher", "maybe")

    assert isolated_db.get_feedback(user_a) == {
        "software-engineer": "interested"
    }
    assert isolated_db.get_feedback(user_b) == {
        "teacher": "maybe"
    }


def test_database_rejects_records_for_nonexistent_users(isolated_db):
    with isolated_db.get_conn() as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("""
                INSERT INTO assessments
                (user_id, created_at, answers_json, profile_json,
                 analysis_json, plan_json)
                VALUES (999999, 'test', '{}', '{}', '{}', '[]')
            """)

@pytest.mark.parametrize(
    "invalid_time",
    ["not-a-time", "25:61", "9:00", "12:90", "99:99"]
)
def test_invalid_reminder_time_preserves_existing_value(
    isolated_db, invalid_time
):
    user_id = isolated_db.create_user("reminder@test.local", "test_hash")

    original = isolated_db.get_settings(user_id)["reminder_time"]

    updated = isolated_db.update_settings(
        user_id,
        reminder_time=invalid_time
    )

    assert updated["reminder_time"] == original


def test_valid_reminder_time_is_saved(isolated_db):
    user_id = isolated_db.create_user("validreminder@test.local", "test_hash")

    updated = isolated_db.update_settings(
        user_id,
        reminder_time="18:45"
    )

    assert updated["reminder_time"] == "18:45"
