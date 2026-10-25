"""career_changer.py - Career transition analysis"""


def _load_careers():
    try:
        import engine
        return {c["id"]: c for c in engine.CAREERS}
    except Exception:
        return {}


def _find_career(query, careers):
    if not query:
        return None
    query_lower = query.lower().strip()
    if query_lower in careers:
        return careers[query_lower]
    for cid, career in careers.items():
        if career.get("title", "").lower() == query_lower:
            return career
    best = None
    best_score = 0
    for cid, career in careers.items():
        title = career.get("title", "").lower()
        if query_lower in title or title in query_lower:
            score = len(set(query_lower.split()) & set(title.split())) / max(1, len(query_lower.split()))
            if score > best_score:
                best_score = score
                best = career
    return best


def _skill_names(career):
    return [s for s in career.get("skills", []) if isinstance(s, str)]


def analyze_transition(current_career, target_career, user_profile):
    current_skills = set(_skill_names(current_career))
    target_skills = set(_skill_names(target_career))
    shared = current_skills & target_skills
    to_gain = target_skills - current_skills
    to_lose = current_skills - target_skills
    user_skills = user_profile.get("skills", {})

    skill_gaps = []
    for skill in to_gain:
        current_level = user_skills.get(skill, 2)
        needed = 4
        if current_level < needed:
            skill_gaps.append({"skill": skill, "current": current_level, "needed": needed, "gap": needed - current_level})
    skill_gaps.sort(key=lambda x: x["gap"], reverse=True)

    total_gap = sum(g["gap"] for g in skill_gaps)
    if total_gap >= 8:
        difficulty, time_weeks = "high", 36
    elif total_gap >= 5:
        difficulty, time_weeks = "medium", 24
    elif total_gap >= 2:
        difficulty, time_weeks = "moderate", 16
    else:
        difficulty, time_weeks = "low", 8

    overlap = len(shared) / max(1, len(target_skills)) if target_skills else 0
    education = target_career.get("education", "Not specified")

    bridge_plan = [
        {"phase": "Phase 1: Foundation (Weeks 1-4)", "title": "Learn the language of the field",
         "action": f"Read 2 books or take 1 intro course on {target_career.get('title', 'the target field')}.",
         "target": "Be able to explain 5 things this role does that outsiders don't know"}
    ]

    if skill_gaps:
        top_gaps = skill_gaps[:3]
        gap_text = ", ".join(g["skill"] for g in top_gaps)
        bridge_plan.append({
            "phase": "Phase 2: Skill Building (Weeks 5-16)",
            "title": f"Build foundational skills: {gap_text}",
            "action": f"Focus 1-2 hours daily on {gap_text}. Do small projects. Document your work publicly.",
            "target": f"Move each skill from ~{top_gaps[0]['current']}/5 to {top_gaps[0]['needed']}/5"
        })

    bridge_plan.append({
        "phase": "Phase 3: Real-World Experience (Weeks 17-24)",
        "title": "Get your first paid or volunteer experience",
        "action": f"Look for internships, freelance work, or volunteer projects in {target_career.get('title', 'the target field')}.",
        "target": "Complete 1 real project with real users"
    })
    bridge_plan.append({
        "phase": "Phase 4: Full Transition (Weeks 25+)",
        "title": "Apply, network, and make the move",
        "action": f"Build your professional network in {target_career.get('title', 'the target field')}.",
        "target": "Land your first role or make the transition official"
    })

    risks = [
        "You may need to take a temporary salary cut during the transition.",
        f"The field requires: {education}" if education else "Education requirements vary.",
        f"You'll be competing with people who started earlier. Your edge is your {len(shared)} transferable skills.",
    ]
    if difficulty == "high":
        risks.append("This is a significant career change - expect 6-12 months of dedicated effort.")

    success_factors = [
        f"Your {len(shared)} shared skills give you a head start",
        f"Your experience from {current_career.get('title', 'your current role')} is valuable",
        "Focused practice beats scattered learning - go deep on 2-3 skills",
    ]

    transferable = []
    for skill in shared:
        level = user_skills.get(skill, 0)
        if level >= 3:
            transferable.append({"skill": skill, "strength": level})

    return {
        "current_career": {"id": current_career.get("id"), "title": current_career.get("title"), "cluster": current_career.get("cluster")},
        "target_career": {"id": target_career.get("id"), "title": target_career.get("title"), "cluster": target_career.get("cluster"), "education": education},
        "overlap_ratio": round(overlap * 100, 1),
        "difficulty": difficulty,
        "estimated_weeks": time_weeks,
        "estimated_months": round(time_weeks / 4),
        "shared_skills": list(shared),
        "transferable_skills": transferable,
        "skills_to_gain": list(to_gain)[:10],
        "skill_gaps": skill_gaps[:5],
        "skills_to_let_go": list(to_lose)[:5],
        "bridge_plan": bridge_plan,
        "risks": risks,
        "success_factors": success_factors,
        "disclaimer": "This is a plan, not a promise. Real transition timelines depend on your effort, network, and market conditions.",
    }
