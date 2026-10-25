"""Milto AI - Career exploration and self-awareness web app (Clean v2)"""
import json
import os
import re
import secrets
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

import db
import engine

# NEW: Security modules
from security import setup_security
from logger import setup_logging, log

load_dotenv()

try:
    import requests
except ImportError:
    requests = None

# ============================================================
# APP SETUP
# ============================================================
app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = os.environ.get("MILTO_SECRET_KEY") or secrets.token_hex(32)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_DOMAIN=None,
    SESSION_COOKIE_PATH="/",
    MAX_CONTENT_LENGTH=512 * 1024,
    PERMANENT_SESSION_LIFETIME=86400 * 7,
    SESSION_REFRESH_EACH_REQUEST=True,
)

CORS(
    app,
    supports_credentials=True,
    origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_headers=["Content-Type", "Authorization", "Cookie"],
    expose_headers=["Set-Cookie"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    max_age=3600,
)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
AI_MODEL = os.environ.get("MILTO_AI_MODEL", "llama-3.3-70b-versatile")


def get_api_type():
    if not ANTHROPIC_API_KEY:
        return "none"
    if ANTHROPIC_API_KEY.startswith('gsk_'):
        return "groq"
    if ANTHROPIC_API_KEY.startswith('sk-'):
        return "openai"
    return "anthropic"


print("=" * 60)
print("MILTO AI DEBUG")
print("=" * 60)
print(f"ANTHROPIC_API_KEY: {'SET' if ANTHROPIC_API_KEY else 'NOT SET'}")
if ANTHROPIC_API_KEY:
    print(f"  Key prefix: {ANTHROPIC_API_KEY[:10]}...")
    print(f"  Detected API: {get_api_type()}")
print(f"AI_MODEL: {AI_MODEL}")
print(f"requests: {'OK' if requests else 'MISSING'}")
print("=" * 60)

# Setup security (rate limiting + headers + error handlers)
limiter = setup_security(app)

# Setup logging
DEBUG = os.environ.get("MILTO_DEBUG", "1") == "1"
setup_logging(debug=DEBUG)

db.init_db()


# ============================================================
# SECURITY
# ============================================================
@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if request.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


# ============================================================
# HELPERS
# ============================================================
def current_user_id():
    return session.get("user_id")


def require_login():
    uid = current_user_id()
    return db.get_user_by_id(uid) if uid else None


def error(msg, code=400):
    return jsonify({"error": msg}), code


def today_key():
    return date.today().isoformat()


def get_latest_or_error(user):
    latest = db.get_latest_assessment(user["id"])
    if not latest:
        return None, error("Complete the assessment first.", 400)
    return latest, None


# ============================================================
# AI SERVICES
# ============================================================
def _groq_text(system_prompt, user_payload, max_tokens=800):
    if not ANTHROPIC_API_KEY or not requests:
        return None
    if isinstance(user_payload, dict):
        user_content = json.dumps(user_payload, ensure_ascii=False)
    else:
        user_content = str(user_payload)
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {ANTHROPIC_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": AI_MODEL or "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_prompt[:4000]},
                    {"role": "user", "content": user_content[:4000]}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            },
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Groq error: {e}")
        return None


def _openai_text(system_prompt, user_payload, max_tokens=800):
    if not ANTHROPIC_API_KEY or not requests:
        return None
    if isinstance(user_payload, dict):
        user_content = json.dumps(user_payload, ensure_ascii=False)
    else:
        user_content = str(user_payload)
    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {ANTHROPIC_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": AI_MODEL or "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt[:4000]},
                    {"role": "user", "content": user_content[:4000]}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            },
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"OpenAI error: {e}")
        return None


def _anthropic_text(system_prompt, user_payload, max_tokens=800):
    if not ANTHROPIC_API_KEY or not requests:
        return None
    if isinstance(user_payload, dict):
        user_content = json.dumps(user_payload, ensure_ascii=False)
    else:
        user_content = str(user_payload)
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": AI_MODEL or "claude-3-sonnet-20240229",
                "max_tokens": max_tokens,
                "system": system_prompt[:4000],
                "messages": [{"role": "user", "content": user_content[:4000]}]
            },
            timeout=30
        )
        resp.raise_for_status()
        content = resp.json().get("content", [])
        return "".join(b.get("text", "") for b in content if b.get("type") == "text").strip()
    except Exception as e:
        print(f"Anthropic error: {e}")
        return None


def _ai_text(system_prompt, user_payload, max_tokens=800):
    if not ANTHROPIC_API_KEY or not requests:
        return None
    api_type = get_api_type()
    if api_type == "groq":
        return _groq_text(system_prompt, user_payload, max_tokens)
    elif api_type == "openai":
        return _openai_text(system_prompt, user_payload, max_tokens)
    elif api_type == "anthropic":
        return _anthropic_text(system_prompt, user_payload, max_tokens)
    return None


def _safe_json_object(text):
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else None
    except Exception:
        return None


# ============================================================
# ROUTES: ROOT
# ============================================================
@app.route("/")
def index():
    return jsonify({
        "name": "Milto AI",
        "version": "2.0",
        "status": "running",
        "api_type": get_api_type(),
        "message": "Milto AI backend is running. Frontend should be at http://localhost:5173"
    })


# ============================================================
# ROUTES: AUTH
# ============================================================
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not 5 <= len(email) <= 120 or "@" not in email:
        return error("Valid email address required.")
    if len(password) < 8 or len(password) > 200:
        return error("Password must be between 8 and 200 characters.")
    if db.get_user_by_email(email):
        return error("That email is already registered.")

    user_id = db.create_user(email, generate_password_hash(password))
    session.clear()
    session["user_id"] = user_id
    session.permanent = True
    return jsonify({"id": user_id, "email": email})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    user = db.get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return error("Incorrect email or password.", 401)

    session.clear()
    session["user_id"] = user["id"]
    session.permanent = True
    return jsonify({"id": user["id"], "email": user["email"]})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


@app.route("/api/me")
def me():
    user = require_login()
    if not user:
        return jsonify({"user": None})
    settings = db.get_settings(user["id"])
    return jsonify({
        "user": {
            "id": user["id"],
            "email": user["email"],
            "created_at": user["created_at"]
        },
        "settings": settings,
    })


# ============================================================
# ROUTES: SETTINGS
# ============================================================
@app.route("/api/settings", methods=["GET", "PUT"])
def settings():
    user = require_login()
    if not user:
        return error("Log in first.", 401)
    if request.method == "GET":
        return jsonify({"settings": db.get_settings(user["id"])})

    data = request.get_json(silent=True) or {}
    theme = data.get("theme")
    enabled = data.get("notifications_enabled")
    reminder = data.get("reminder_time")
    style = data.get("motivation_style")

    if theme is not None and theme not in ("dark", "light"):
        return error("Invalid theme.")
    if reminder is not None and not re.match(r"^([01]\d|2[0-3]):[0-5]\d$", str(reminder)):
        return error("Invalid reminder time.")
    if style is not None and style not in ("gentle", "direct", "celebrate"):
        return error("Invalid motivation style.")

    updated = db.update_settings(user["id"], theme, enabled, reminder, style)
    return jsonify({"settings": updated})


# ============================================================
# ROUTES: META
# ============================================================
@app.route("/api/meta")
def meta():
    return jsonify({
        "questions": engine.QUESTIONS,
        "skills": engine.SKILLS,
        "values": engine.VALUES,
        "riasecMeta": engine.RIASEC_META,
        "bigFiveMeta": engine.BIG_FIVE_META,
        "stages": engine.STAGES,
    })


@app.route("/api/ai-status")
def ai_status():
    ai_available = bool(ANTHROPIC_API_KEY and requests)
    return jsonify({
        "externalLLM": ai_available,
        "api_type": get_api_type(),
        "model": AI_MODEL,
        "localML": bool(engine.CAREER_VECTORIZER),
        "status": "ready" if ai_available else "limited",
    })


@app.route("/api/debug-ai", methods=["GET", "POST"])
def debug_ai():
    if not ANTHROPIC_API_KEY or not requests:
        return jsonify({
            "error": "API not configured",
            "api_key_set": bool(ANTHROPIC_API_KEY),
            "requests_available": bool(requests)
        })
    if request.method == "GET":
        return jsonify({
            "api_type": get_api_type(),
            "model": AI_MODEL,
            "status": "configured"
        })
    data = request.get_json(silent=True) or {}
    test_message = data.get("message", "Say hello")
    try:
        response = _ai_text("You are a helpful assistant. Be brief.", {"message": test_message}, 100)
        return jsonify({
            "success": bool(response),
            "api_type": get_api_type(),
            "response": response
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# ============================================================
# ROUTES: ASSESSMENT
# ============================================================
@app.route("/api/assessment", methods=["POST"])
def submit_assessment():
    user = require_login()
    if not user:
        return error("Log in first.", 401)

    data = request.get_json(silent=True) or {}
    answers = data.get("answers") or {}

    if not answers.get("stage"):
        return error("Answer where you are right now before continuing.")

    profile = engine.score_answers(answers)
    analysis = engine.analyze_10_levels(profile)
    ranked = engine.recommend(profile, {}, limit=10)
    plan = engine.generate_plan(profile, ranked, answers.get("stage"))
    activities = engine.generate_activities(profile, answers, ranked, answers.get("stage"))

    assessment_id = db.save_assessment(
        user["id"], answers, profile, plan, activities, analysis
    )

    return jsonify({
        "id": assessment_id,
        "profile": profile,
        "analysis": analysis,
        "recommendations": engine.serialize_ranked(ranked),
        "plan": plan,
        "activities": activities,
        "activityDone": {},
        "activityFeedback": {},
        "hollandCode": "".join(engine.holland_code(profile)),
        "hollandNarrative": engine.holland_narrative(profile),
    })


@app.route("/api/results")
def get_results():
    user = require_login()
    if not user:
        return error("Log in first.", 401)
    latest = db.get_latest_assessment(user["id"])
    if not latest:
        return jsonify({"assessment": None})
    feedback = db.get_feedback(user["id"])
    ranked = engine.recommend(latest["profile"], feedback, limit=10)
    return jsonify({
        "assessment": {
            "id": latest["id"],
            "created_at": latest["created_at"],
            "answers": latest["answers"],
            "profile": latest["profile"],
            "analysis": latest.get("analysis", {}),
            "plan": latest["plan"],
            "taskDone": latest["task_done"],
            "activities": latest["activities"],
            "activityDone": latest["activity_done"],
            "activityFeedback": latest.get("activity_feedback", {}),
        },
        "recommendations": engine.serialize_ranked(ranked),
        "feedback": feedback,
        "hollandCode": "".join(engine.holland_code(latest["profile"])),
        "hollandNarrative": engine.holland_narrative(latest["profile"]),
    })


@app.route("/api/history")
def get_history():
    user = require_login()
    if not user:
        return error("Log in first.", 401)
    out = []
    for h in db.get_history(user["id"]):
        ranked = engine.recommend(h["profile"], {}, limit=1)
        out.append({
            "id": h["id"],
            "created_at": h["created_at"],
            "hollandCode": "".join(engine.holland_code(h["profile"])),
            "topCareer": ranked[0]["career"]["title"] if ranked else None,
        })
    return jsonify({"history": out})


# ============================================================
# ROUTES: TASKS
# ============================================================
@app.route("/api/task", methods=["POST"])
def toggle_task():
    user = require_login()
    if not user:
        return error("Log in first.", 401)
    latest, err = get_latest_or_error(user)
    if err:
        return err
    data = request.get_json(silent=True) or {}
    idx = str(data.get("index"))
    if not idx.isdigit() or int(idx) >= len(latest["plan"]):
        return error("Unknown plan task.")
    task_done = latest["task_done"]
    task_done[idx] = bool(data.get("done"))
    db.update_task_done(latest["id"], task_done)
    return jsonify({"taskDone": task_done})


@app.route("/api/activity/complete", methods=["POST"])
def complete_activity():
    user = require_login()
    if not user:
        return error("Log in first.", 401)
    latest, err = get_latest_or_error(user)
    if err:
        return err

    data = request.get_json(silent=True) or {}
    activity_id = str(data.get("activityId") or "")
    difficulty = str(data.get("difficulty") or "just-right")
    note = str(data.get("note") or "").strip()[:500]

    if difficulty not in ("too-easy", "just-right", "too-hard"):
        return error("Invalid difficulty feedback.")

    valid = {str(a.get("id")) for a in latest["activities"]}
    if activity_id not in valid:
        return error("Unknown activity.")

    done = latest["activity_done"]
    done[activity_id] = True
    feedback = latest.get("activity_feedback", {})
    feedback[activity_id] = {"difficulty": difficulty, "note": note}

    db.update_activity_done(latest["id"], done)
    db.update_activity_feedback(latest["id"], feedback)

    ranked = engine.recommend(latest["profile"], db.get_feedback(user["id"]), limit=5)
    history = [
        {"id": a.get("id"), "title": a.get("title"),
         "difficulty": feedback.get(a.get("id"), {}).get("difficulty")}
        for a in latest["activities"] if done.get(a.get("id"))
    ]

    next_activity = engine.fallback_adaptive_activity(
        latest["profile"], latest["answers"], ranked, history, feedback
    )

    existing_ids = {a.get("id") for a in latest["activities"]}
    if next_activity.get("id") in existing_ids:
        next_activity["id"] = f"{next_activity['id']}-next-{len(latest['activities']) + 1}"

    latest["activities"].append(next_activity)
    latest["activities"] = latest["activities"][-15:]
    db.update_activities(latest["id"], latest["activities"])

    return jsonify({
        "activityDone": done,
        "activityFeedback": feedback,
        "nextActivity": next_activity,
        "activities": latest["activities"],
    })


@app.route("/api/activity", methods=["POST"])
def toggle_activity():
    user = require_login()
    if not user:
        return error("Log in first.", 401)
    latest, err = get_latest_or_error(user)
    if err:
        return err
    data = request.get_json(silent=True) or {}
    activity_id = str(data.get("activityId") or "")
    if activity_id not in {str(a.get("id")) for a in latest["activities"]}:
        return error("Unknown activity.")
    done = latest["activity_done"]
    done[activity_id] = bool(data.get("done"))
    db.update_activity_done(latest["id"], done)
    return jsonify({"activityDone": done})


# ============================================================
# ROUTES: FEEDBACK
# ============================================================
@app.route("/api/feedback", methods=["POST"])
def submit_feedback():
    user = require_login()
    if not user:
        return error("Log in first.", 401)
    data = request.get_json(silent=True) or {}
    career_id = data.get("careerId")
    rating = data.get("rating")

    if not career_id or career_id not in engine.CAREER_BY_ID:
        return error("Unknown career.")
    if rating not in ("interested", "maybe", "not_for_me", None):
        return error("Invalid rating.")

    db.set_feedback(user["id"], career_id, rating)
    latest = db.get_latest_assessment(user["id"])
    feedback = db.get_feedback(user["id"])
    ranked = engine.recommend(latest["profile"], feedback, limit=10) if latest else []
    return jsonify({
        "feedback": feedback,
        "recommendations": engine.serialize_ranked(ranked)
    })


# ============================================================
# ROUTES: BRUTAL HONESTY & LIMITATIONS
# ============================================================

@app.route("/api/limitations", methods=["POST"])
def analyze_limitations():
    """Analyze gaps between user profile and dream career"""
    user = require_login()
    if not user:
        return error("Log in first.", 401)
    
    data = request.get_json(silent=True) or {}
    target_career_query = str(data.get("career") or "").strip()[:100]
    
    if not target_career_query:
        return error("Tell me your dream career.")
    
    latest, err = get_latest_or_error(user)
    if err: return err

    # Use the existing career changer logic to find the career
    from modules import career_changer
    careers = career_changer._load_careers()
    target_career = career_changer._find_career(target_career_query, careers)
    
    if not target_career:
        return error("Career not found in our database.")

    user_profile = latest["profile"]
    user_skills = user_profile.get("skills", {})
    user_interests = user_profile.get("interests", {})
    
    # Calculate limitations
    limitations = []
    
    # 1. Skill gaps
    career_skills = target_career.get("skills", [])
    for skill in career_skills:
        user_level = user_skills.get(skill, 1)
        if user_level < 4:
            limitations.append({
                "type": "skill",
                "area": skill,
                "current": user_level,
                "required": 4,
                "severity": "high" if user_level <= 2 else "medium",
                "message": f"Your {skill} is at {user_level}/5. You need at least 4/5."
            })
    
    # 2. Interest mismatch (RIASEC)
    career_riasec = target_career.get("riasec", {})
    for dim, required_score in career_riasec.items():
        if required_score >= 4: # Career requires high interest in this
            user_score = user_interests.get(dim, 50) / 20 # Normalize to 1-5
            if user_score < 3:
                limitations.append({
                    "type": "interest",
                    "area": dim,
                    "current": round(user_score, 1),
                    "required": 4,
                    "severity": "high",
                    "message": f"Your interest in this area is low ({round(user_score,1)}/5). You might find the daily work boring."
                })

    # Sort by severity
    limitations.sort(key=lambda x: (x["severity"] == "high", x["current"]), reverse=True)
    
    return jsonify({
        "target_career": target_career.get("title"),
        "readiness_score": max(0, 100 - (len(limitations) * 10)),
        "limitations": limitations[:8], # Top 8
        "message": "Fix these to be ready." if limitations else "You have no major limitations! Start applying."
    })


@app.route("/api/coach/brutal", methods=["POST"])
def coach_brutal():
    """Brutal Honesty Coach"""
    user = require_login()
    if not user:
        return error("Log in first.", 401)
    
    data = request.get_json(silent=True) or {}
    message = str(data.get("message") or "").strip()[:2000]
    intensity = data.get("intensity", "direct") # gentle, direct, brutal
    
    latest, err = get_latest_or_error(user)
    if err: return err
    
    ranked = engine.recommend(latest["profile"], db.get_feedback(user["id"]), limit=3)
    top_career = ranked[0]["career"]["title"] if ranked else "Unknown"
    
    # Build the persona prompt
    base_prompt = "You are Milto, an AI career coach. "
    if intensity == "brutal":
        persona = "You are ruthless, blunt, and intolerant of excuses. Do not sugarcoat. Point out exactly what the user is doing wrong or what they lack. Use harsh words to push them to action. Be direct and aggressive but not insulting."
    elif intensity == "direct":
        persona = "You are professional, direct, and no-nonsense. Give straight facts. Do not use fluff. Focus on action."
    else:
        persona = "You are warm, encouraging, and supportive. Frame challenges as opportunities."

    system_prompt = base_prompt + persona + " Do not use emojis. Keep it under 3 paragraphs."
    
    context = {
        "top_career": top_career,
        "user_skills": latest["profile"].get("skills", {}),
        "user_question": message
    }

    reply = _ai_text(system_prompt, context, 400)
    
    if not reply:
        # Fallback based on intensity
        if intensity == "brutal":
            reply = f"Your top career is {top_career}. Stop asking questions and start doing the work. You lack skills. Fix them."
        else:
            reply = f"Your top career is {top_career}. Focus on building the skills you lack."
            
    db.add_chat_message(user["id"], "assistant", reply)
    return jsonify({"reply": reply, "intensity": intensity})

# ============================================================
# ROUTES: EXPLORE PATH
# ============================================================
@app.route("/api/explore-path", methods=["POST"])
def explore_path():
    user = require_login()
    if not user:
        return error("Log in first.", 401)
    data = request.get_json(silent=True) or {}
    desired = str(data.get("interest") or "").strip()[:240]
    if len(desired) < 2:
        return error("Tell Milto the career you want to explore.")
    latest, err = get_latest_or_error(user)
    if err:
        return err
    result = engine.explore_user_path(latest["profile"], desired, db.get_feedback(user["id"]))
    result["aiGeneratedExplanation"] = False
    if result.get("matchedCareer") and ANTHROPIC_API_KEY and requests:
        safe = engine.ai_context_for_path(latest["profile"], result)
        system = (
            "You are Milto Path Analyst. Improve the explanation of a user's desired career path. "
            "Return valid JSON only with keys: overview, fit_explanation, difficulty_explanation, "
            "practice_strategy, encouragement. Never claim certainty."
        )
        candidate = _safe_json_object(_ai_text(system, safe, 700))
        if candidate:
            result["aiExplanation"] = candidate
            result["aiGeneratedExplanation"] = True
    return jsonify(result)


# ============================================================
# ROUTES: COACH
# ============================================================
def build_coach_context(profile, answers, ranked, message):
    skills = profile.get("skills", {})
    sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)
    top_skills = [{"skill": s, "level": l} for s, l in sorted_skills[:5]]
    weak_skills = [{"skill": s, "level": l} for s, l in sorted_skills[-5:] if l < 3]

    interests = profile.get("interests", {})
    top_interests = sorted(interests.items(), key=lambda x: x[1], reverse=True)[:3]

    top_careers = []
    for r in ranked[:3]:
        top_careers.append({
            "title": r["career"]["title"],
            "score": r.get("match_percentage", round(r["score"] * 100))
        })

    return {
        "user_profile": {
            "holland_code": "".join(engine.holland_code(profile)),
            "top_interests": [{"code": k, "name": engine.RIASEC_META.get(k, {}).get("label", k)}
                              for k, v in top_interests],
            "top_strengths": top_skills,
            "areas_to_improve": weak_skills,
            "personality": profile.get("personality", {}),
            "goal": answers.get("goals", ""),
            "stage": answers.get("stage", "")
        },
        "career_context": {
            "top_recommendations": top_careers,
        },
        "user_question": message
    }


@app.route("/api/coach", methods=["POST"])
def coach():
    user = require_login()
    if not user:
        return error("Log in first.", 401)
    data = request.get_json(silent=True) or {}
    message = str(data.get("message") or "").strip()[:2000]
    if not message:
        return error("Empty message.")
    latest, err = get_latest_or_error(user)
    if err:
        return err
    ranked = engine.recommend(latest["profile"], db.get_feedback(user["id"]), limit=5)
    db.add_chat_message(user["id"], "user", message)
    context = build_coach_context(latest["profile"], latest["answers"], ranked, message)
    system_prompt = """You are Milto, a warm and practical career exploration coach for Ethiopian university students.
Use profile data as one signal, not destiny. Suggest small experiments. Be specific.
Reference Ethiopian universities and job market when relevant. Keep responses concise (2-4 paragraphs)."""
    reply = None
    source = "local-ai"
    if ANTHROPIC_API_KEY and requests:
        try:
            ai_response = _ai_text(system_prompt, context, 700)
            if ai_response:
                reply = ai_response
                source = "generative-ai"
        except Exception as e:
            print(f"Coach AI error: {e}")
    if not reply:
        top = ranked[0]["career"]["title"] if ranked else "a career you want to test"
        reply = (
            f"Your current strongest Milto direction is **{top}**. "
            f"If you want to explore a different career, tell me specifically - "
            f"I can map the gap and build a practical bridge plan."
        )
        source = "fallback"
    db.add_chat_message(user["id"], "assistant", reply)
    return jsonify({"reply": reply, "source": source})


# ============================================================
# ROUTES: DAILY
# ============================================================
@app.route("/api/daily")
def daily():
    user = require_login()
    if not user:
        return error("Log in first.", 401)
    requested = request.args.get("date") or today_key()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", requested):
        return error("Invalid date.")
    existing = db.get_daily(user["id"], requested)
    if existing:
        return jsonify({"daily": existing})
    latest = db.get_latest_assessment(user["id"])
    if not latest:
        return jsonify({"daily": None})
    ranked = engine.recommend(latest["profile"], db.get_feedback(user["id"]), limit=5)
    completed = len([x for x, v in latest["activity_done"].items() if v])
    content = engine.generate_daily_content(
        latest["profile"], latest["answers"], ranked, requested, completed_count=completed
    )
    item = db.create_daily(user["id"], requested, content["self_awareness"], content["plan"])
    return jsonify({"daily": item})


@app.route("/api/daily/task", methods=["POST"])
def daily_task():
    user = require_login()
    if not user:
        return error("Log in first.", 401)
    data = request.get_json(silent=True) or {}
    day_key = data.get("date") or today_key()
    item = db.get_daily(user["id"], day_key)
    if not item:
        return error("Complete the assessment first.", 400)
    task_id = str(data.get("taskId") or "")
    valid = {x.get("id") for x in item["plan"]}
    if task_id not in valid:
        return error("Unknown daily task.")
    done = item["done"]
    done[task_id] = bool(data.get("done"))
    updated = db.update_daily_done(user["id"], day_key, done)
    return jsonify({"daily": updated})


# ============================================================
# ROUTES: REFLECTIONS
# ============================================================
@app.route("/api/reflections", methods=["GET", "POST"])
def reflections():
    user = require_login()
    if not user:
        return error("Log in first.", 401)
    if request.method == "GET":
        return jsonify({"reflections": db.get_reflections(user["id"], 60)})
    data = request.get_json(silent=True) or {}
    prompt = str(data.get("prompt") or "").strip()[:500]
    response = str(data.get("response") or "").strip()[:2000]
    day_key = data.get("date") or today_key()
    if not prompt or not response:
        return error("Write a reflection before saving it.")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", day_key):
        return error("Invalid date.")
    rid = db.add_reflection(user["id"], day_key, prompt, response)
    return jsonify({
        "id": rid,
        "reflections": db.get_reflections(user["id"], 60)
    })


# ============================================================
# ROUTES: ETHIOPIAN CONTEXT
# ============================================================
def _load_ethiopian_data():
    """Load Ethiopian data files"""
    base = Path(__file__).parent / "data" / "ethiopian"
    data = {}
    for name in ["universities", "programs", "career_context"]:
        f = base / f"{name}.json"
        if f.exists():
            with open(f, "r", encoding="utf-8") as fh:
                data[name] = json.load(fh)
        else:
            data[name] = {} if name != "universities" else []
    return data


@app.route("/api/ethiopian/universities")
def ethiopian_universities():
    """List all Ethiopian universities"""
    data = _load_ethiopian_data()
    return jsonify({"universities": data.get("universities", [])})


@app.route("/api/ethiopian/programs")
def ethiopian_programs():
    """List all program mappings"""
    data = _load_ethiopian_data()
    return jsonify({"programs": data.get("programs", {})})


@app.route("/api/ethiopian/career/<career_id>")
def ethiopian_career_context(career_id):
    """Get Ethiopian context for a specific career"""
    data = _load_ethiopian_data()
    context = data.get("career_context", {}).get(career_id, {})
    if not context:
        return jsonify({"error": "No Ethiopian context for this career"}), 404
    return jsonify({"career_id": career_id, "context": context})

# ============================================================
# RUN
# ============================================================

# ============================================================
# ROUTES: CAREER CHANGE
# ============================================================
@app.route("/api/career-change", methods=["POST"])
def career_change():
    """Analyze a career transition"""
    user = require_login()
    if not user:
        return error("Log in first.", 401)

    data = request.get_json(silent=True) or {}
    current_query = str(data.get("current") or "").strip()[:100]
    target_query = str(data.get("target") or "").strip()[:100]

    if not current_query or not target_query:
        return error("Provide both current and target careers.")

    latest, err = get_latest_or_error(user)
    if err:
        return err

    from modules import career_changer
    careers = career_changer._load_careers()

    current_career = career_changer._find_career(current_query, careers)
    target_career = career_changer._find_career(target_query, careers)

    if not current_career:
        return error(f"Could not find current career: {current_query}")
    if not target_career:
        return error(f"Could not find target career: {target_query}")

    analysis = career_changer.analyze_transition(
        current_career, target_career, latest["profile"]
    )
    return jsonify(analysis)



# ============================================================
# ROUTES: PERSONAL DEVELOPMENT
# ============================================================
@app.route("/api/development/plan", methods=["POST"])
def personal_development_plan():
    user = require_login()
    if not user:
        return error("Log in first.", 401)
    data = request.get_json(silent=True) or {}
    goal_query = str(data.get("goal") or "").strip()[:100]
    if not goal_query:
        return error("Tell me what you want to develop.")
    latest, err = get_latest_or_error(user)
    if err:
        return err
    from modules import personal_development
    plan = personal_development.create_development_plan(goal_query, latest["profile"])
    if "error" in plan:
        return jsonify(plan), 400
    return jsonify(plan)


@app.route("/api/development/traits")
def list_traits():
    from modules import personal_development
    return jsonify({
        "traits": [{"id": k, **v} for k, v in personal_development.TRAIT_LIBRARY.items()],
        "skills": [{"id": k, **v} for k, v in personal_development.SKILL_LIBRARY.items()],
    })




# ============================================================
# ROUTES: NOTIFICATIONS
# ============================================================
@app.route("/api/notifications", methods=["GET"])
def get_notifications():
    """Get pending notifications for the user"""
    user = require_login()
    if not user:
        return error("Log in first.", 401)

    latest = db.get_latest_assessment(user["id"])
    if not latest:
        return jsonify({"notifications": [], "count": 0})

    notifications = []

    # 1. Check today's daily tasks
    from datetime import date
    today = date.today().isoformat()
    daily = db.get_daily(user["id"], today)

    if daily:
        done_tasks = daily.get("done", {})
        plan = daily.get("plan", [])
        pending = [t for t in plan if not done_tasks.get(t.get("id"))]
        if pending:
            notifications.append({
                "id": "daily-pending",
                "type": "activity",
                "title": f"You have {len(pending)} pending tasks today",
                "body": f"Complete: {pending[0].get('title')}",
                "icon": "📋",
                "action_url": "/dashboard",
                "created_at": today
            })

    # 2. Check pending activities
    activities = latest.get("activities", [])
    done_activities = latest.get("activity_done", {})
    pending_activities = [a for a in activities if not done_activities.get(a.get("id"))]
    if pending_activities:
        notifications.append({
            "id": "activity-pending",
            "type": "activity",
            "title": f"{len(pending_activities)} activities waiting",
            "body": pending_activities[0].get("title", "New activity"),
            "icon": "🎯",
            "action_url": "/dashboard",
            "created_at": today
        })

    # 3. Weekly check-in reminder
    from datetime import datetime, timedelta
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    reflections = db.get_reflections(user["id"], 1)
    if not reflections or (reflections and reflections[0].get("created_at", "") < week_ago):
        notifications.append({
            "id": "reflection-reminder",
            "type": "reflection",
            "title": "Time for a weekly reflection",
            "body": "Take 5 minutes to write what you learned this week.",
            "icon": "✍️",
            "action_url": "/dashboard",
            "created_at": today
        })

    return jsonify({
        "notifications": notifications,
        "count": len(notifications)
    })


@app.route("/api/notifications/dismiss", methods=["POST"])
def dismiss_notification():
    """Mark a notification as dismissed"""
    user = require_login()
    if not user:
        return error("Log in first.", 401)

    data = request.get_json(silent=True) or {}
    notification_id = data.get("id")
    if not notification_id:
        return error("Missing notification ID.")

    # For now, just return success (we could store dismissed IDs in DB later)
    return jsonify({"ok": True, "dismissed": notification_id})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("MILTO_DEBUG", "1") == "1"
    app.run(host="127.0.0.1", port=port, debug=debug, use_reloader=False)
