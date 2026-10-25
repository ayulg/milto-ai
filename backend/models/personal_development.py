"""personal_development.py - Plan to develop personality traits and skills"""

TRAIT_LIBRARY = {
    "extraversion": {"name": "Extraversion", "description": "Becoming more social, energetic, and comfortable around people"},
    "introversion": {"name": "Introversion", "description": "Becoming more comfortable with solitude and quiet focus"},
    "conscientiousness": {"name": "Conscientiousness", "description": "Becoming more organized, disciplined, and reliable"},
    "openness": {"name": "Openness", "description": "Becoming more curious, creative, and open to new experiences"},
    "agreeableness": {"name": "Agreeableness", "description": "Becoming more compassionate, cooperative, and empathetic"},
    "emotional_stability": {"name": "Emotional Stability", "description": "Becoming more calm, resilient, and less reactive"},
    "assertiveness": {"name": "Assertiveness", "description": "Becoming more confident, direct, and able to speak up"},
    "discipline": {"name": "Discipline", "description": "Becoming more consistent, focused, and able to follow through"},
    "leadership": {"name": "Leadership", "description": "Becoming more able to influence and guide others"},
    "empathy": {"name": "Empathy", "description": "Becoming more able to understand others' feelings"},
    "creativity": {"name": "Creativity", "description": "Becoming more inventive, original, and generative"},
    "confidence": {"name": "Confidence", "description": "Becoming more self-assured and trusting in your abilities"},
}

SKILL_LIBRARY = {
    "programming": {"name": "Programming", "description": "Writing software, debugging, problem-solving with code", "resources": ["FreeCodeCamp", "CS50 by Harvard", "LeetCode", "The Odin Project"]},
    "writing": {"name": "Writing", "description": "Clear prose, reports, stories", "resources": ["On Writing Well", "The Elements of Style", "Hemingway app", "Daily 500-word journaling"]},
    "communication": {"name": "Communication", "description": "Speaking, presenting, explaining ideas", "resources": ["Toastmasters", "TED Talks", "Crucial Conversations"]},
    "leadership": {"name": "Leadership", "description": "Setting direction, coaching, taking responsibility", "resources": ["Leaders Eat Last", "Start with Why", "7 Habits of Highly Effective People"]},
    "data": {"name": "Data Analysis", "description": "Analyzing data, statistics, visualization", "resources": ["Kaggle Learn", "Google Data Analytics", "Introduction to Statistical Learning"]},
    "design": {"name": "Design", "description": "Visual design, UX, layout, aesthetics", "resources": ["Design of Everyday Things", "Refactoring UI", "Figma tutorials"]},
    "research": {"name": "Research", "description": "Finding and synthesizing information", "resources": ["Google Scholar", "The Craft of Research", "Zotero"]},
    "public_speaking": {"name": "Public Speaking", "description": "Presenting, speaking up, handling nerves", "resources": ["Toastmasters", "TED Masterclass", "Speaking Up Without Freaking Out"]},
    "finance": {"name": "Financial Literacy", "description": "Budgeting, investing, understanding money", "resources": ["The Psychology of Money", "Khan Academy Finance", "The Index Card"]},
    "networking": {"name": "Networking", "description": "Building relationships and finding mentors", "resources": ["How to Win Friends", "Never Eat Alone", "LinkedIn optimization"]},
}

def _find_trait(query):
    if not query:
        return None
    q = query.lower().strip().replace(" ", "_")
    if q in TRAIT_LIBRARY:
        return q, TRAIT_LIBRARY[q]
    aliases = {"social": "extraversion", "outgoing": "extraversion", "organized": "conscientiousness", "curious": "openness", "kind": "agreeableness", "calm": "emotional_stability", "confident": "confidence", "assertive": "assertiveness"}
    for alias, tid in aliases.items():
        if alias in q:
            return tid, TRAIT_LIBRARY[tid]
    for tid, trait in TRAIT_LIBRARY.items():
        if q in tid or tid in q:
            return tid, trait
    return None

def _find_skill(query):
    if not query:
        return None
    q = query.lower().strip().replace(" ", "_")
    if q in SKILL_LIBRARY:
        return q, SKILL_LIBRARY[q]
    for sid, skill in SKILL_LIBRARY.items():
        if q in sid or sid in q:
            return sid, skill
    return None

def build_12_week_plan(goal_id, goal_data, user_profile):
    is_skill = goal_data.get("resources") is not None
    name = goal_data.get("name", goal_id)
    description = goal_data.get("description", "")
    if is_skill:
        weekly = _skill_weeks(name)
        habits = _skill_habits(name)
        resources = goal_data.get("resources", [])
        milestones = _skill_milestones(name)
    else:
        weekly = _trait_weeks(name, goal_id)
        habits = _trait_habits(goal_id)
        resources = _trait_resources(goal_id)
        milestones = _trait_milestones(name, goal_id)
    return {
        "goal_id": goal_id, "goal_name": name, "goal_description": description,
        "goal_type": "skill" if is_skill else "trait",
        "timeline_weeks": 12, "weekly_activities": weekly,
        "daily_habits": habits, "resources": resources, "milestones": milestones,
    }

def _skill_weeks(name):
    return [
        {"week": 1, "theme": "Foundation", "activity": f"Learn basics of {name.lower()}. 30 min/day.", "focus": "fundamentals"},
        {"week": 2, "theme": "Foundation", "activity": f"Continue learning. Take notes.", "focus": "consistency"},
        {"week": 3, "theme": "Foundation", "activity": f"Complete a beginner project.", "focus": "first output"},
        {"week": 4, "theme": "Foundation", "activity": f"Review notes. Identify weak areas.", "focus": "self-awareness"},
        {"week": 5, "theme": "Practice", "activity": f"Practice 45 min/day. Harder exercises.", "focus": "depth"},
        {"week": 6, "theme": "Practice", "activity": f"Build a medium project. Ask for feedback.", "focus": "feedback"},
        {"week": 7, "theme": "Practice", "activity": f"Study how experts work.", "focus": "modeling"},
        {"week": 8, "theme": "Practice", "activity": f"Teach someone else.", "focus": "consolidation"},
        {"week": 9, "theme": "Real-world", "activity": f"Work on a real project.", "focus": "applied"},
        {"week": 10, "theme": "Real-world", "activity": f"Get feedback. Iterate.", "focus": "improvement"},
        {"week": 11, "theme": "Real-world", "activity": f"Build a portfolio piece.", "focus": "evidence"},
        {"week": 12, "theme": "Real-world", "activity": f"Reflect on 12 weeks.", "focus": "reflection"},
    ]

def _skill_habits(name):
    return [f"30 min of {name.lower()} practice daily", "Read one article weekly", "Journal daily", "Share work publicly weekly", "Ask for feedback weekly"]

def _skill_milestones(name):
    return [
        {"week": 4, "milestone": f"Complete beginner {name.lower()} project", "evidence": "shared link"},
        {"week": 8, "milestone": f"Explain {name.lower()} to someone", "evidence": "recorded session"},
        {"week": 12, "milestone": f"Build portfolio piece", "evidence": "portfolio entry"},
    ]

def _trait_weeks(name, trait_id):
    return [
        {"week": 1, "theme": "Awareness", "activity": f"Track when {name.lower()} shows up.", "focus": "observation"},
        {"week": 2, "theme": "Awareness", "activity": f"Read 1 book on {name.lower()}.", "focus": "learning"},
        {"week": 3, "theme": "Awareness", "activity": f"Take one small action today.", "focus": "first step"},
        {"week": 4, "theme": "Awareness", "activity": f"Ask 2 people for feedback.", "focus": "external feedback"},
        {"week": 5, "theme": "Practice", "activity": f"Do one uncomfortable thing daily.", "focus": "exposure"},
        {"week": 6, "theme": "Practice", "activity": f"Practice in low-stakes setting.", "focus": "safe practice"},
        {"week": 7, "theme": "Practice", "activity": f"Practice in medium-stakes setting.", "focus": "escalation"},
        {"week": 8, "theme": "Practice", "activity": f"Practice in high-stakes setting.", "focus": "challenge"},
        {"week": 9, "theme": "Integration", "activity": f"Notice when it comes naturally.", "focus": "recognition"},
        {"week": 10, "theme": "Integration", "activity": f"Teach someone else.", "focus": "consolidation"},
        {"week": 11, "theme": "Integration", "activity": f"Reflect on changes.", "focus": "reflection"},
        {"week": 12, "theme": "Integration", "activity": f"Set a new small goal.", "focus": "sustainability"},
    ]

def _trait_habits(trait_id):
    habits = {
        "extraversion": ["Say hi to one stranger daily", "Join one group per week", "Reach out to one friend daily"],
        "introversion": ["30 min alone daily", "Read weekly", "Journal evening"],
        "conscientiousness": ["Plan tomorrow tonight", "Hardest task first", "Weekly review Sunday"],
        "openness": ["Try one new thing weekly", "Read outside genre", "New podcast weekly"],
        "agreeableness": ["One act of kindness daily", "Listen without interrupting", "Thank someone daily"],
        "emotional_stability": ["5-min meditation morning", "3 gratitudes daily", "Exercise 3x/week"],
        "assertiveness": ["Speak first in one meeting weekly", "Say no once weekly", "State one opinion daily"],
        "leadership": ["Own one task", "Mentor weekly", "Read leadership book monthly"],
        "empathy": ["Ask how are you really daily", "Listen without solving", "Volunteer weekly"],
        "creativity": ["Write 100 words daily", "Sketch daily", "Combine two ideas"],
        "confidence": ["Write 3 wins daily", "Do one scary thing weekly", "Speak up daily"],
        "discipline": ["Wake same time daily", "30-day habit", "No phone first hour"],
    }
    return habits.get(trait_id, ["Practice daily", "Track progress", "Reflect weekly"])

def _trait_resources(trait_id):
    resources = {
        "extraversion": ["How to Win Friends by Dale Carnegie", "Quiet by Susan Cain", "Toastmasters"],
        "introversion": ["Quiet by Susan Cain", "The Introvert Advantage", "Journaling"],
        "conscientiousness": ["Atomic Habits", "The Power of Habit", "Getting Things Done"],
        "openness": ["Range by David Epstein", "Where Good Ideas Come From", "Curiosity"],
        "agreeableness": ["Nonviolent Communication", "How to Win Friends", "Just Mercy"],
        "emotional_stability": ["The Anxiety Workbook", "Feeling Good", "Headspace"],
        "assertiveness": ["When I Say No", "Crucial Conversations", "Nonviolent Communication"],
        "leadership": ["Leaders Eat Last", "7 Habits", "Dare to Lead"],
        "empathy": ["Nonviolent Communication", "Daring Greatly", "The Empathy Exams"],
        "creativity": ["The Artist's Way", "Steal Like an Artist", "Bird by Bird"],
        "confidence": ["The Confidence Code", "Presence", "Daring Greatly"],
        "discipline": ["Atomic Habits", "Deep Work", "The War of Art"],
    }
    return resources.get(trait_id, ["Atomic Habits", "The Power of Habit"])

def _trait_milestones(name, trait_id):
    return [
        {"week": 4, "milestone": f"Articulate 5 examples of {name.lower()}", "evidence": "reflection"},
        {"week": 8, "milestone": f"3 uncomfortable actions completed", "evidence": "log"},
        {"week": 12, "milestone": f"Others notice difference", "evidence": "feedback"},
    ]

def create_development_plan(goal_query, user_profile):
    if not goal_query or len(goal_query.strip()) < 2:
        return {"error": "Tell me what you want to develop"}
    trait_result = _find_trait(goal_query)
    if trait_result:
        tid, tdata = trait_result
        return build_12_week_plan(tid, tdata, user_profile)
    skill_result = _find_skill(goal_query)
    if skill_result:
        sid, sdata = skill_result
        return build_12_week_plan(sid, sdata, user_profile)
    # Any other non-empty goal gets a practical general-purpose skill plan.
    # This makes the feature useful for careers and skills beyond the curated catalog
    # (for example dancing, nursing, teaching, carpentry, or a software tool).
    normalized = " ".join(goal_query.strip().split())[:100]
    generic = {
        "name": normalized[:1].upper() + normalized[1:],
        "description": f"Build practical ability in {normalized} through structured learning, deliberate practice, feedback, and a small real-world project.",
        "resources": [
            f"Beginner learning materials for {normalized}",
            f"A practice project or exercise set for {normalized}",
            "A trusted teacher, mentor, peer, or community for feedback",
        ],
    }
    goal_id = "custom_" + "_".join(normalized.lower().split())[:60]
    plan = build_12_week_plan(goal_id, generic, user_profile)
    plan["goal_type"] = "skill"
    plan["custom_goal"] = True
    plan["planning_note"] = "This is a general learning framework. Adjust the exercises, safety requirements, and resources to your field and experience level."
    return plan
