"""
Core engine for Milto AI
Handles scoring, recommendations, and analysis
"""
import json
import math
import os
from pathlib import Path

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:
    TfidfVectorizer = None
    cosine_similarity = None

DATA_DIR = Path(__file__).parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"

# Load core data files
with open(DATA_DIR / "careers.json", encoding="utf-8") as f:
    CAREERS = json.load(f)
with open(DATA_DIR / "questions.json", encoding="utf-8") as f:
    QUESTIONS = json.load(f)
with open(DATA_DIR / "meta.json", encoding="utf-8") as f:
    _meta = json.load(f)

SKILLS = _meta["SKILLS"]
VALUES = _meta["VALUES"]
RIASEC_META = _meta["RIASEC_META"]
BIG_FIVE_META = _meta["BIG_FIVE_META"]
STAGES = _meta["STAGES"]

CAREER_BY_ID = {c["id"]: c for c in CAREERS}
SKILL_BY_ID = {s["id"]: s for s in SKILLS}
VALUE_BY_ID = {v["id"]: v for v in VALUES}

RIASEC = ["R", "I", "A", "S", "E", "C"]
BIG = ["O", "C", "E", "A", "N"]


# ============ TEXT SEARCH ============
CAREER_DOCUMENTS = [
    " ".join([
        c.get("title", ""), c.get("cluster", ""), c.get("summary", ""),
        c.get("dayInLife", ""), c.get("education", ""),
        " ".join(c.get("skills", [])), " ".join(c.get("values", [])),
    ]) for c in CAREERS
]

CAREER_VECTORIZER = None
CAREER_MATRIX = None

if TfidfVectorizer and cosine_similarity:
    try:
        CAREER_VECTORIZER = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
        CAREER_MATRIX = CAREER_VECTORIZER.fit_transform(CAREER_DOCUMENTS)
    except Exception:
        CAREER_VECTORIZER = CAREER_MATRIX = None


def clamp(n, lo=0, hi=100):
    return max(lo, min(hi, n))


def mean(xs):
    if not xs:
        return 50
    return sum(xs) / len(xs)


def likert_to_100(value, reverse=False):
    v = 6 - value if reverse else value
    return ((v - 1) / 4) * 100


# ============ SCORING ============
def empty_scores():
    return {
        "personality": {k: 50 for k in BIG},
        "interests": {k: 50 for k in RIASEC},
        "skills": {s["id"]: 3 for s in SKILLS},
        "values": {v["id"]: 3 for v in VALUES},
    }


def score_answers(answers):
    """Score assessment answers into a profile"""
    scores = empty_scores()
    p_buckets = {k: [] for k in BIG}
    i_buckets = {k: [] for k in RIASEC}

    for q in QUESTIONS:
        raw = answers.get(q["id"])
        if raw is None or raw == "":
            continue
        section = q["section"]
        trait = q.get("trait")
        if section == "personality" and trait and isinstance(raw, (int, float)):
            p_buckets[trait].append(likert_to_100(raw, q.get("reverse", False)))
        elif section == "interests" and trait and isinstance(raw, (int, float)):
            i_buckets[trait].append(likert_to_100(raw, q.get("reverse", False)))
        elif section == "skills" and trait and isinstance(raw, (int, float)):
            scores["skills"][trait] = raw
        elif section == "values" and trait and isinstance(raw, (int, float)):
            scores["values"][trait] = raw

    for k in BIG:
        scores["personality"][k] = round(mean(p_buckets[k]))
    for k in RIASEC:
        scores["interests"][k] = round(mean(i_buckets[k]))

    return scores


# ============ 10-LEVEL ANALYSIS ============
def analyze_10_levels(profile):
    """
    Analyze personality at 10 levels with match rates
    Returns dict with all 10 levels and scores
    """
    analysis = {}
    
    # Level 1: Trait Distribution
    personality = profile.get('personality', {})
    trait_scores = {
        'Openness': personality.get('O', 50),
        'Conscientiousness': personality.get('C', 50),
        'Extraversion': personality.get('E', 50),
        'Agreeableness': personality.get('A', 50),
        'Emotional Stability': 100 - personality.get('N', 50)
    }
    analysis['level_1'] = {
        'name': 'Trait Distribution',
        'score': round(mean(list(trait_scores.values()))),
        'details': trait_scores,
        'description': 'Your Big Five personality traits'
    }
    
    # Level 2: Interest Pattern
    interests = profile.get('interests', {})
    top_interests = sorted(interests.items(), key=lambda x: x[1], reverse=True)[:3]
    analysis['level_2'] = {
        'name': 'Interest Pattern',
        'score': round(mean([v for k, v in top_interests])),
        'details': {k: v for k, v in top_interests},
        'description': 'Your top 3 career interests (RIASEC)'
    }
    
    # Level 3: Skill Profile
    skills = profile.get('skills', {})
    top_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)[:5]
    analysis['level_3'] = {
        'name': 'Skill Profile',
        'score': round(mean([v * 20 for k, v in top_skills])),
        'details': {k: v * 20 for k, v in top_skills},
        'description': 'Your strongest skills'
    }
    
    # Level 4: Value Alignment
    values = profile.get('values', {})
    top_values = sorted(values.items(), key=lambda x: x[1], reverse=True)[:3]
    analysis['level_4'] = {
        'name': 'Value Alignment',
        'score': round(mean([v * 20 for k, v in top_values])),
        'details': {k: v * 20 for k, v in top_values},
        'description': 'What matters most to you'
    }
    
    # Level 5: Work Style
    work_style_score = (personality.get('C', 50) + personality.get('E', 50)) / 2
    analysis['level_5'] = {
        'name': 'Work Style',
        'score': round(work_style_score),
        'details': {
            'structure': personality.get('C', 50),
            'social': personality.get('E', 50),
            'style': 'structured' if work_style_score > 60 else 'flexible'
        },
        'description': 'How you prefer to work'
    }
    
    # Level 6: Environment Fit
    env_score = (personality.get('O', 50) + personality.get('E', 50)) / 2
    analysis['level_6'] = {
        'name': 'Environment Fit',
        'score': round(env_score),
        'details': {
            'openness': personality.get('O', 50),
            'social_preference': personality.get('E', 50),
            'environment': 'dynamic' if env_score > 60 else 'stable'
        },
        'description': 'Your ideal work environment'
    }
    
    # Level 7: Career Readiness
    readiness = (personality.get('C', 50) + mean([v * 20 for k, v in top_skills])) / 2
    analysis['level_7'] = {
        'name': 'Career Readiness',
        'score': round(readiness),
        'details': {
            'discipline': personality.get('C', 50),
            'skills': mean([v * 20 for k, v in top_skills]),
            'readiness': 'high' if readiness > 70 else 'developing' if readiness > 50 else 'building'
        },
        'description': 'Your readiness for career challenges'
    }
    
    # Level 8: Growth Potential
    growth = (personality.get('O', 50) + 100 - personality.get('N', 50)) / 2
    analysis['level_8'] = {
        'name': 'Growth Potential',
        'score': round(growth),
        'details': {
            'openness': personality.get('O', 50),
            'resilience': 100 - personality.get('N', 50),
            'potential': 'high' if growth > 70 else 'moderate'
        },
        'description': 'Your capacity for personal growth'
    }
    
    # Level 9: Market Alignment
    top_skills_list = [s for s, v in top_skills if v >= 4]
    market_score = min(100, len(top_skills_list) * 20)
    analysis['level_9'] = {
        'name': 'Market Alignment',
        'score': market_score,
        'details': {
            'marketable_skills': top_skills_list,
            'count': len(top_skills_list)
        },
        'description': 'How well your skills align with market needs'
    }
    
    # Level 10: Overall Fit
    all_scores = [
        analysis['level_1']['score'],
        analysis['level_2']['score'],
        analysis['level_3']['score'],
        analysis['level_4']['score'],
        analysis['level_5']['score'],
        analysis['level_6']['score'],
        analysis['level_7']['score'],
        analysis['level_8']['score'],
        analysis['level_9']['score'],
    ]
    analysis['level_10'] = {
        'name': 'Overall Fit',
        'score': round(mean(all_scores)),
        'details': {
            'summary': 'comprehensive profile assessment',
            'levels_completed': 10
        },
        'description': 'Your overall career readiness score'
    }
    
    return analysis


# ============ MATCHING ============
def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if not na or not nb:
        return 0
    return dot / (na * nb)


def user_riasec_vec(p):
    return [p["interests"][k] / 20 for k in RIASEC]


def career_riasec_vec(c):
    return [c["riasec"][k] for k in RIASEC]


def user_big_vec(p):
    out = []
    for k in BIG:
        v = p["personality"][k] / 20
        out.append(6 - v if k == "N" else v)
    return out


def career_big_vec(c):
    return [c["bigFive"][k] for k in BIG]


def skill_overlap(c, p):
    if not c["skills"]:
        return 0.5
    avg = mean([p["skills"].get(s, 3) for s in c["skills"]])
    return (avg - 1) / 4


def value_match(c, p):
    if not c["values"]:
        return 0.5
    avg = mean([p["values"].get(v, 3) for v in c["values"]])
    return (avg - 1) / 4


def holland_code(p):
    return sorted(RIASEC, key=lambda k: p["interests"][k], reverse=True)[:3]


def career_holland(c):
    return sorted(RIASEC, key=lambda k: c["riasec"][k], reverse=True)[:3]


def explain_career(career, profile):
    """Generate explanation for a career match"""
    reasons = []
    user_code = holland_code(profile)
    job_code = career_holland(career)
    shared = [k for k in job_code if k in user_code]
    
    if shared:
        reasons.append(
            "Your interest pattern ({}) overlaps this role's {} core.".format(
                " · ".join(RIASEC_META[k]["short"] for k in user_code),
                " / ".join(RIASEC_META[k]["label"].lower() for k in job_code),
            )
        )

    trait_notes = []
    p, cf = profile["personality"], career["bigFive"]
    if p["O"] >= 65 and cf["O"] >= 4:
        trait_notes.append("high openness — you will not mind a field that keeps changing")
    if p["C"] >= 65 and cf["C"] >= 4:
        trait_notes.append("follow-through — this work rewards people who finish")
    if p["E"] >= 65 and cf["E"] >= 4:
        trait_notes.append("social energy — the role is built around other people")
    elif p["E"] <= 40 and cf["E"] <= 3:
        trait_notes.append("a quieter tempo — deep work is more of the day than performance")
    if p["A"] >= 65 and cf["A"] >= 4:
        trait_notes.append("a cooperative bent — the work is relational, not purely adversarial")
    if p["N"] <= 40 and cf["N"] <= 2:
        trait_notes.append("steadiness under pressure, which this path periodically needs")
    
    if trait_notes:
        reasons.append("Personality fit: {}.".format("; ".join(trait_notes[:2])))

    strong_skills = [s for s in career["skills"] if profile["skills"].get(s, 0) >= 4]
    if strong_skills:
        labels = [SKILL_BY_ID.get(s, {}).get("label", s).lower() for s in strong_skills[:3]]
        reasons.append(f"You already bring {', '.join(labels)} — skills this role uses every week.")

    top_values = sorted(VALUES, key=lambda v: profile["values"].get(v["id"], 0), reverse=True)[:2]
    top_value_ids = [v["id"] for v in top_values]
    value_hit = [v for v in career["values"] if v in top_value_ids]
    if value_hit:
        labels = [VALUE_BY_ID.get(v, {}).get("label", v).lower() for v in value_hit]
        reasons.append(f"It speaks to what you said you need: {' and '.join(labels)}.")

    if not reasons:
        reasons.append(
            "This is a plausible exploration path — not a perfect twin of your profile, "
            "but close enough to be worth a closer look."
        )
    return reasons[:4]


def skill_gaps(career, profile):
    gaps = [
        {"skill": s, "have": profile["skills"].get(s, 1), "need": 4}
        for s in career["skills"]
    ]
    gaps = [g for g in gaps if g["have"] < g["need"]]
    gaps.sort(key=lambda g: g["have"])
    return gaps


def skill_strengths(career, profile):
    return [s for s in career["skills"] if profile["skills"].get(s, 0) >= 4]


def recommend(profile, feedback=None, limit=10):
    """Recommend careers with match scores"""
    feedback = feedback or {}
    ranked = []
    
    for career in CAREERS:
        interest = cosine(user_riasec_vec(profile), career_riasec_vec(career))
        personality = cosine(user_big_vec(profile), career_big_vec(career))
        skills = skill_overlap(career, profile)
        values = value_match(career, profile)
        score = 0.4 * interest + 0.25 * personality + 0.2 * skills + 0.15 * values

        fb = feedback.get(career["id"])
        if fb == "interested":
            score += 0.08
        if fb == "maybe":
            score += 0.02
        if fb == "not_for_me":
            score -= 0.28

        for rel in career.get("related", []):
            if feedback.get(rel) == "interested":
                score += 0.03
            if feedback.get(rel) == "not_for_me":
                score -= 0.04

        score = clamp(score, 0, 1)
        ranked.append({
            "career": career,
            "score": score,
            "match_percentage": round(score * 100),
            "reasons": explain_career(career, profile),
            "gaps": skill_gaps(career, profile),
            "strengths": skill_strengths(career, profile),
        })

    ranked.sort(key=lambda r: r["score"], reverse=True)
    return ranked[:limit]


def serialize_ranked(ranked):
    return [
        {
            "career": r["career"],
            "score": round(r["score"], 4),
            "match_percentage": r["match_percentage"],
            "reasons": r["reasons"],
            "gaps": r["gaps"],
            "strengths": r["strengths"],
        }
        for r in ranked
    ]


def holland_narrative(profile):
    code = holland_code(profile)
    ranks = ["leading", "supporting", "third"]
    return "; ".join(
        f"{RIASEC_META[k]['label']} ({RIASEC_META[k]['short']}) is {ranks[i]}"
        for i, k in enumerate(code)
    )


def generate_plan(profile, top, stage=None):
    """Generate a personal development plan"""
    tasks = []
    primary = top[0] if len(top) > 0 else None
    secondary = top[1] if len(top) > 1 else None

    code_line = "; ".join(
        f"{RIASEC_META[k]['label']} — {RIASEC_META[k]['short']}" for k in holland_code(profile)
    )
    tasks.append({
        "title": "Name the pattern, not the job",
        "description": f"Write half a page on the three interest types that lead your map "
                        f"({code_line}). Where have they already shown up in school, work, or hobbies?",
        "category": "awareness",
        "careerId": None,
    })

    if primary:
        tasks.append({
            "title": f"A day in the life of a {primary['career']['title'].lower()}",
            "description": "Read two first-person accounts (blog, podcast, or informational "
                            "interview notes) of this role. Capture: what they actually do, what "
                            "drains them, and one thing that surprised you.",
            "category": "exploration",
            "careerId": primary["career"]["id"],
        })

    gap = primary["gaps"][0] if primary and primary["gaps"] else None
    if gap:
        skill = SKILL_BY_ID.get(gap["skill"], {})
        tasks.append({
            "title": f"Raise {skill.get('label', gap['skill']).lower()} one notch",
            "description": f"You rated this {gap['have']}/5; {primary['career']['title'].lower()} "
                            f"typically needs closer to {gap['need']}. Pick a 3-hour practice: a "
                            f"tutorial, a short project, or a class session. Evidence beats intention.",
            "category": "skill",
            "careerId": primary["career"]["id"],
        })

    if secondary:
        primary_title = primary["career"]["title"] if primary else "your top match"
        tasks.append({
            "title": f"Hold a second path: {secondary['career']['title']}",
            "description": f"List three ways this role is different from {primary_title} — and "
                            f"one way it is the same. You are mapping a region, not picking a single peak.",
            "category": "exploration",
            "careerId": secondary["career"]["id"],
        })

    tasks.append({
        "title": "Talk to one person who does the work",
        "description": (
            "Ask a professor, alumni office, or family friend for a 20-minute conversation. "
            "Three questions: how they got in, what they misunderstood at your age, what they "
            "would learn this year if they were you."
        ),
        "category": "network",
        "careerId": primary["career"]["id"] if primary else None,
    })

    return tasks[:7]


def generate_activities(profile, answers, top, stage=None):
    """Generate activities based on profile"""
    activities = []
    primary = top[0]["career"] if top else None
    top_interest = sorted(RIASEC, key=lambda k: profile["interests"][k], reverse=True)[0]
    top_value = max(VALUES, key=lambda v: profile["values"].get(v["id"], 0), default=None)
    low_trait = min(BIG, key=lambda k: profile["personality"].get(k, 50))
    weakest_skill = min(SKILLS, key=lambda x: profile["skills"].get(x["id"], 3), default=None)

    activities.append({
        "id": "energy-check",
        "title": "Your energy map",
        "type": "reflection",
        "duration": "5 min",
        "difficulty": "Easy",
        "prompt": "Think about the last 7 days. Write down one activity that gave you energy and one that drained you. What was different about them?",
        "why": f"Your strongest interest signal is {RIASEC_META[top_interest]['label'].lower()}, so noticing what naturally energizes you can make that pattern more concrete.",
        "goal": answers.get("goals") or "Understand what kinds of work fit me",
    })

    if weakest_skill:
        label = weakest_skill["label"]
        activities.append({
            "id": "micro-skill-" + weakest_skill["id"],
            "title": f"One tiny step in {label}",
            "type": "growth",
            "duration": "15 min",
            "difficulty": "Easy",
            "prompt": f"Choose one {label.lower()} task you can practice for only 15 minutes. Do it before you feel ready, then rate your confidence before and after from 1–5.",
            "why": f"You currently rate {label.lower()} at {profile['skills'].get(weakest_skill['id'], 3)}/5. Small experiments turn a self-rating into evidence.",
            "goal": answers.get("goals") or "Build confidence in my skills",
        })

    if primary:
        activities.append({
            "id": "career-reality-test",
            "title": f"Reality-test {primary['title']}",
            "type": "exploration",
            "duration": "20 min",
            "difficulty": "Medium",
            "prompt": f"Find one real project, job description, video, or interview about {primary['title']}. Write: 2 things that excite you, 1 thing that worries you, and 1 question you still have.",
            "why": "A career match becomes useful when you compare the idea of a career with its real daily work.",
            "goal": answers.get("goals") or "Explore my best-fit career paths",
        })

    return activities[:5]


def minimal_ai_profile(profile, answers, ranked, activity_history=None):
    """Minimal context for AI"""
    weakest = sorted(SKILLS, key=lambda x: profile["skills"].get(x["id"], 3))[:3]
    strongest = sorted(SKILLS, key=lambda x: profile["skills"].get(x["id"], 3), reverse=True)[:3]
    interests = sorted(RIASEC, key=lambda k: profile["interests"].get(k, 0), reverse=True)[:3]
    values = sorted(VALUES, key=lambda x: profile["values"].get(x["id"], 0), reverse=True)[:3]
    return {
        "goal": (answers.get("goals") or "").strip()[:500],
        "stage": answers.get("stage"),
        "strengths": [{"skill": x["label"], "rating": profile["skills"].get(x["id"], 3)} for x in strongest],
        "improvement_areas": [{"skill": x["label"], "rating": profile["skills"].get(x["id"], 3)} for x in weakest],
        "interests": [RIASEC_META[k]["label"] for k in interests],
        "values": [x["label"] for x in values],
        "holland_code": "".join(holland_code(profile)),
        "top_careers": [r["career"]["title"] for r in ranked[:3]],
        "recent_activity": (activity_history or [])[-5:],
    }


def fallback_adaptive_activity(profile, answers, ranked, history=None, feedback=None):
    """Fallback activity when AI is unavailable"""
    history = history or []
    feedback = feedback or {}
    primary = ranked[0]["career"] if ranked else None
    weak = min(SKILLS, key=lambda x: profile["skills"].get(x["id"], 3), default=None)
    
    if weak:
        skill = weak["label"]
        rating = profile["skills"].get(weak["id"], 3)
        difficulty = "Easy" if rating <= 2 else "Medium"
        return {
            "id": f"adaptive-{weak['id']}-{len(history)+1}",
            "title": f"Adaptive practice: {skill}",
            "type": "adaptive growth",
            "duration": "10–20 min",
            "difficulty": difficulty,
            "prompt": f"Spend 15 minutes practicing {skill.lower()} on a tiny, concrete example related to {primary['title'] if primary else 'your goal'}. Finish with one sentence describing what became easier.",
            "why": f"Your current self-rating is {rating}/5, so Milto is targeting this improvement area with a small step instead of a large course.",
            "goal": (answers.get("goals") or "Build useful skills and confidence")[:300],
            "adaptive": True,
            "source": "milto-fallback",
        }
    
    return {
        "id": f"adaptive-reflection-{len(history)+1}",
        "title": "Adaptive reflection",
        "type": "adaptive awareness",
        "duration": "10 min",
        "difficulty": "Easy",
        "prompt": "Write one thing you learned from your last activity, one thing you would change, and one tiny action you will repeat.",
        "why": "Milto uses reflection to turn completed actions into better next steps.",
        "goal": (answers.get("goals") or "Build self-awareness")[:300],
        "adaptive": True,
        "source": "milto-fallback"
    }


def generate_daily_content(profile, answers, ranked, day_key, completed_count=0):
    """Generate daily content"""
    weak = min(SKILLS, key=lambda s: profile.get("skills", {}).get(s["id"], 3), default=None)
    strong = max(SKILLS, key=lambda s: profile.get("skills", {}).get(s["id"], 3), default=None)
    top_value = max(VALUES, key=lambda v: profile.get("values", {}).get(v["id"], 3), default=None)
    career = ranked[0]["career"] if ranked else None
    cycle = sum(ord(ch) for ch in str(day_key)) % 4
    goal = (answers.get("goals") or "understand myself and build useful skills").strip()[:300]

    prompts = [
        f"What is one moment today when you felt naturally engaged or curious? What were you doing, and what might that reveal about your interests?",
        f"Where did you notice yourself using {strong['label'].lower()} today? Write one concrete example and what it tells you about your current strengths." if strong else "What felt easier than expected today? Why do you think it felt easier?",
        f"What is one situation today where you could have practiced {weak['label'].lower()}? Describe a smaller version you could try tomorrow." if weak else "What is one skill you would like to make easier through practice?",
        f"Did an activity today support your value of {top_value['label'] if top_value else 'growth'}? What would you change next time?",
    ]
    prompt = prompts[cycle]

    tasks = []
    if weak:
        tasks.append({
            "id": f"daily-skill-{day_key}",
            "title": f"15-minute {weak['label']} practice",
            "description": f"Do one tiny practice related to {weak['label'].lower()} and finish with one sentence about what improved.",
            "category": "Growth",
            "duration": "15 min",
        })
    if career:
        tasks.append({
            "id": f"daily-career-{day_key}",
            "title": f"Reality-check {career['title']}",
            "description": f"Spend 10 minutes examining one real task, project, or job description related to {career['title']}. Save one thing that attracts you and one question.",
            "category": "Career exploration",
            "duration": "10 min",
        })
    tasks.append({
        "id": f"daily-goal-{day_key}",
        "title": "One tiny move toward your goal",
        "description": f"Choose one action that moves you toward: {goal}",
        "category": "Goal",
        "duration": "10–20 min",
    })

    return {
        "day_key": day_key,
        "self_awareness": {"prompt": prompt, "theme": ["Curiosity", "Strengths", "Growth", "Values"][cycle]},
        "plan": tasks[:3],
    }


def explore_user_path(profile, desired, feedback=None):
    """Explore a specific career path chosen by the user"""
    desired = (desired or "").strip()[:240]
    
    # Simple search
    matches = []
    desired_lower = desired.lower()
    for c in CAREERS:
        title = c.get('title', '').lower()
        summary = c.get('summary', '').lower()
        if desired_lower in title or title in desired_lower:
            matches.append((c, 0.9))
        elif desired_lower in summary:
            matches.append((c, 0.6))
    
    if not matches:
        return {
            "query": desired,
            "matchedCareer": None,
            "fit": 0,
            "status": "needs-research",
            "message": "Milto could not map this interest to its current career knowledge base yet.",
            "steps": [],
            "difficulties": []
        }
    
    best, score = matches[0]
    ranked = recommend(profile, feedback or {}, limit=len(CAREERS))
    profile_fit = next((r for r in ranked if r["career"]["id"] == best["id"]), None)
    fit = float(profile_fit["score"] if profile_fit else 0)
    combined = clamp(round((0.55 * fit + 0.45 * min(score, 1)) * 100), 0, 100)
    
    gaps = skill_gaps(best, profile)
    strengths = skill_strengths(best, profile)
    
    difficulties = []
    if gaps:
        difficulties.append(f"You may need to build {', '.join(SKILL_BY_ID.get(g['skill'], {}).get('label', g['skill']).lower() for g in gaps[:3])} before you feel job-ready.")
    if best.get("education"):
        difficulties.append(best["education"])
    difficulties.append(f"The daily work may differ from the idea of {best['title'].lower()}: {best.get('dayInLife', '')}")
    
    steps = []
    for i, g in enumerate(gaps[:4], 1):
        label = SKILL_BY_ID.get(g["skill"], {}).get("label", g["skill"])
        steps.append({
            "week": i,
            "title": f"Build {label}",
            "action": f"Practice {label.lower()} for 3 focused sessions and produce one small piece of evidence.",
            "target": f"Move from {g['have']}/5 toward {g['need']}/5"
        })
    
    steps.append({
        "week": min(6, len(steps) + 1),
        "title": f"Reality-test {best['title']}",
        "action": f"Study one real project or job description for {best['title']} and compare the tasks with what you enjoy.",
        "target": "Write 3 things you would enjoy, 2 difficulties, and 1 open question."
    })
    steps.append({
        "week": min(8, len(steps) + 2),
        "title": "Build proof, not intention",
        "action": f"Create a small beginner project connected to {best['title']} and ask for feedback.",
        "target": "One shareable artifact + one feedback conversation"
    })
    
    reasons = explain_career(best, profile)
    
    return {
        "query": desired,
        "matchedCareer": best,
        "semanticScore": round(score, 4),
        "fit": combined,
        "profileFit": round(fit * 100),
        "status": "strong" if combined >= 70 else "possible" if combined >= 50 else "stretch",
        "reasons": reasons,
        "strengths": strengths,
        "gaps": gaps,
        "difficulties": difficulties[:4],
        "steps": steps[:6],
        "alternatives": [{"title": c["title"], "id": c["id"]} for c, sc in matches[1:4]],
        "disclaimer": "This is a pathway analysis, not a prediction of success."
    }


def ai_context_for_path(profile, path_result):
    """Prepare context for AI"""
    c = path_result.get("matchedCareer") or {}
    return {
        "desired_interest": path_result.get("query", ""),
        "career": {
            "title": c.get("title"),
            "summary": c.get("summary"),
            "day_in_life": c.get("dayInLife"),
            "skills": c.get("skills", [])
        },
        "fit": path_result.get("fit"),
        "strengths": path_result.get("strengths", [])[:5],
        "gaps": path_result.get("gaps", [])[:5],
        "difficulties": path_result.get("difficulties", [])[:4],
        "steps": path_result.get("steps", [])[:6]
    }