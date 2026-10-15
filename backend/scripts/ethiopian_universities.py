"""
ethiopian_universities.py - Ethiopian university and program data
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
ETHIOPIAN_DIR = DATA_DIR / "ethiopian"
ETHIOPIAN_DIR.mkdir(parents=True, exist_ok=True)

def create_universities():
    """Ethiopian universities dataset"""
    universities = [
        {"id": "aau", "name": "Addis Ababa University", "type": "public", "location": "Addis Ababa", "founded": 1950, "ranking": 1, "website": "www.aau.edu.et"},
        {"id": "aait", "name": "Addis Ababa Institute of Technology", "type": "public", "location": "Addis Ababa", "founded": 1953, "ranking": 2, "website": "www.aait.edu.et"},
        {"id": "bdu", "name": "Bahir Dar University", "type": "public", "location": "Bahir Dar", "founded": 2001, "ranking": 3, "website": "www.bdu.edu.et"},
        {"id": "hu", "name": "Hawassa University", "type": "public", "location": "Hawassa", "founded": 1999, "ranking": 4, "website": "www.hu.edu.et"},
        {"id": "mu", "name": "Mekelle University", "type": "public", "location": "Mekelle", "founded": 1991, "ranking": 5, "website": "www.mu.edu.et"},
        {"id": "ju", "name": "Jimma University", "type": "public", "location": "Jimma", "founded": 1999, "ranking": 6, "website": "www.ju.edu.et"},
        {"id": "uog", "name": "University of Gondar", "type": "public", "location": "Gondar", "founded": 1954, "ranking": 7, "website": "www.uog.edu.et"},
        {"id": "haramaya", "name": "Haramaya University", "type": "public", "location": "Haramaya", "founded": 1954, "ranking": 8, "website": "www.haramaya.edu.et"},
        {"id": "amu", "name": "Arba Minch University", "type": "public", "location": "Arba Minch", "founded": 1986, "ranking": 9, "website": "www.amu.edu.et"},
        {"id": "astu", "name": "Adama Science and Technology University", "type": "public", "location": "Adama", "founded": 1993, "ranking": 10, "website": "www.astu.edu.et"},
        {"id": "wku", "name": "Wolkite University", "type": "public", "location": "Wolkite", "founded": 2010, "ranking": 11, "website": "www.wku.edu.et"},
        {"id": "ddu", "name": "Dire Dawa University", "type": "public", "location": "Dire Dawa", "founded": 2006, "ranking": 12, "website": "www.ddu.edu.et"},
        {"id": "smu", "name": "St. Mary's University", "type": "private", "location": "Addis Ababa", "founded": 1998, "ranking": 1, "website": "www.smuc.edu.et"},
        {"id": "uu", "name": "Unity University", "type": "private", "location": "Addis Ababa", "founded": 1991, "ranking": 2, "website": "www.unity.edu.et"},
        {"id": "au", "name": "Admas University", "type": "private", "location": "Addis Ababa", "founded": 1998, "ranking": 3, "website": "www.admas.edu.et"},
        {"id": "rvu", "name": "Rift Valley University", "type": "private", "location": "Addis Ababa", "founded": 2001, "ranking": 4, "website": "www.rvu.edu.et"},
    ]
    return universities


def create_program_mappings():
    """Map Ethiopian university programs to careers"""
    return {
        "Computer Science": {
            "careers": ["software-engineer", "data-scientist", "cybersecurity-analyst"],
            "universities": ["aau", "aait", "bdu", "hu", "smu", "uu", "astu"],
            "duration": 4, "degree": "BSc"
        },
        "Software Engineering": {
            "careers": ["software-engineer", "product-manager"],
            "universities": ["aait", "bdu", "hu", "mu", "astu"],
            "duration": 5, "degree": "BSc"
        },
        "Information Technology": {
            "careers": ["software-engineer", "cybersecurity-analyst", "data-scientist"],
            "universities": ["aau", "smu", "uu", "au", "rvu"],
            "duration": 4, "degree": "BSc"
        },
        "Information Systems": {
            "careers": ["data-scientist", "product-manager", "cybersecurity-analyst"],
            "universities": ["aau", "bdu", "hu", "ju"],
            "duration": 4, "degree": "BSc"
        },
        "Electrical Engineering": {
            "careers": ["software-engineer"],
            "universities": ["aait", "bdu", "hu", "mu", "amu", "astu"],
            "duration": 5, "degree": "BSc"
        },
        "Civil Engineering": {
            "careers": ["architect", "urban-planner"],
            "universities": ["aait", "bdu", "hu", "mu", "amu", "astu"],
            "duration": 5, "degree": "BSc"
        },
        "Mechanical Engineering": {
            "careers": ["architect", "electrician"],
            "universities": ["aait", "bdu", "hu", "mu", "astu"],
            "duration": 5, "degree": "BSc"
        },
        "Medicine": {
            "careers": ["registered-nurse", "clinical-psychologist"],
            "universities": ["aau", "uog", "ju", "hu", "mu"],
            "duration": 6, "degree": "MD"
        },
        "Nursing": {
            "careers": ["registered-nurse", "physical-therapist"],
            "universities": ["aau", "ju", "uog", "haramaya"],
            "duration": 4, "degree": "BSc"
        },
        "Public Health": {
            "careers": ["registered-nurse", "social-worker", "policy-analyst"],
            "universities": ["aau", "ju", "uog", "haramaya"],
            "duration": 4, "degree": "BSc"
        },
        "Pharmacy": {
            "careers": ["registered-nurse", "research-scientist"],
            "universities": ["aau", "uog", "ju"],
            "duration": 5, "degree": "BPharm"
        },
        "Law": {
            "careers": ["lawyer", "policy-analyst"],
            "universities": ["aau", "bdu", "hu", "smu", "uu"],
            "duration": 5, "degree": "LLB"
        },
        "Business Administration": {
            "careers": ["product-manager", "management-consultant", "hr-people-partner", "marketing-manager"],
            "universities": ["aau", "bdu", "hu", "smu", "uu", "au", "rvu"],
            "duration": 4, "degree": "BA"
        },
        "Accounting": {
            "careers": ["financial-analyst", "management-consultant"],
            "universities": ["aau", "bdu", "hu", "smu", "uu"],
            "duration": 4, "degree": "BA"
        },
        "Economics": {
            "careers": ["financial-analyst", "policy-analyst", "data-scientist"],
            "universities": ["aau", "bdu", "hu", "ju"],
            "duration": 4, "degree": "BA"
        },
        "Psychology": {
            "careers": ["clinical-psychologist", "social-worker", "hr-people-partner"],
            "universities": ["aau", "uog", "ju", "hu"],
            "duration": 4, "degree": "BA"
        },
        "Sociology": {
            "careers": ["social-worker", "policy-analyst"],
            "universities": ["aau", "hu", "bdu"],
            "duration": 4, "degree": "BA"
        },
        "Agriculture": {
            "careers": ["environmental-scientist", "urban-planner"],
            "universities": ["haramaya", "ju", "hu", "amu"],
            "duration": 4, "degree": "BSc"
        },
        "Architecture": {
            "careers": ["architect", "urban-planner"],
            "universities": ["aait", "bdu", "mu", "astu"],
            "duration": 5, "degree": "BArch"
        },
        "Journalism": {
            "careers": ["journalist", "writer-strategist"],
            "universities": ["aau", "bdu", "hu"],
            "duration": 4, "degree": "BA"
        },
        "Fine Arts": {
            "careers": ["graphic-designer", "ux-designer"],
            "universities": ["aau", "bdu"],
            "duration": 4, "degree": "BA"
        },
    }


def create_career_context():
    """Ethiopian-specific career context"""
    return {
        "software-engineer": {
            "local_demand": "high",
            "salary_range_etb": "15,000 - 35,000",
            "employers": ["Ethio Telecom", "Commercial Bank of Ethiopia", "Safaricom Ethiopia", "Tech Startups"],
            "top_programs": ["Computer Science", "Software Engineering", "Information Technology"],
            "growth": "very_high"
        },
        "data-scientist": {
            "local_demand": "growing",
            "salary_range_etb": "18,000 - 40,000",
            "employers": ["Commercial Bank of Ethiopia", "Ethiopian Statistical Service", "Tech Startups"],
            "top_programs": ["Computer Science", "Statistics", "Data Science"],
            "growth": "high"
        },
        "cybersecurity-analyst": {
            "local_demand": "high",
            "salary_range_etb": "20,000 - 45,000",
            "employers": ["Ethio Telecom", "Information Network Security Agency (INSA)", "Banks"],
            "top_programs": ["Computer Science", "Cybersecurity", "Information Systems"],
            "growth": "very_high"
        },
        "registered-nurse": {
            "local_demand": "high",
            "salary_range_etb": "10,000 - 25,000",
            "employers": ["Ministry of Health", "AAU Teaching Hospital", "Private Hospitals"],
            "top_programs": ["Nursing", "Public Health"],
            "growth": "high"
        },
        "clinical-psychologist": {
            "local_demand": "growing",
            "salary_range_etb": "15,000 - 35,000",
            "employers": ["Hospitals", "Mental Health Centers", "Private Practice"],
            "top_programs": ["Psychology", "Clinical Psychology"],
            "growth": "growing"
        },
        "lawyer": {
            "local_demand": "stable",
            "salary_range_etb": "15,000 - 40,000",
            "employers": ["Ministry of Justice", "Private Law Firms", "Commercial Bank"],
            "top_programs": ["Law (LLB)"],
            "growth": "stable"
        },
        "financial-analyst": {
            "local_demand": "growing",
            "salary_range_etb": "12,000 - 30,000",
            "employers": ["Commercial Bank of Ethiopia", "NIB Bank", "Ministry of Finance"],
            "top_programs": ["Accounting", "Economics", "Finance"],
            "growth": "growing"
        },
        "architect": {
            "local_demand": "stable",
            "salary_range_etb": "15,000 - 35,000",
            "employers": ["Construction Companies", "Urban Development Offices", "Private Firms"],
            "top_programs": ["Architecture"],
            "growth": "stable"
        },
        "teacher-k12": {
            "local_demand": "high",
            "salary_range_etb": "8,000 - 18,000",
            "employers": ["Ministry of Education", "Private Schools", "Regional Bureaus"],
            "top_programs": ["Education", "Subject-specific (BA + Teaching Certificate)"],
            "growth": "stable"
        },
        "product-manager": {
            "local_demand": "growing",
            "salary_range_etb": "20,000 - 50,000",
            "employers": ["Tech Startups", "Ethio Telecom", "Banks"],
            "top_programs": ["Business Administration", "Computer Science", "Engineering"],
            "growth": "high"
        },
    }


def main():
    print("="*60)
    print("🇪🇹 CREATING ETHIOPIAN UNIVERSITY DATA")
    print("="*60)

    universities = create_universities()
    with open(ETHIOPIAN_DIR / "universities.json", "w", encoding="utf-8") as f:
        json.dump(universities, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(universities)} universities")

    programs = create_program_mappings()
    with open(ETHIOPIAN_DIR / "programs.json", "w", encoding="utf-8") as f:
        json.dump(programs, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(programs)} program mappings")

    context = create_career_context()
    with open(ETHIOPIAN_DIR / "career_context.json", "w", encoding="utf-8") as f:
        json.dump(context, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(context)} career contexts")

    print("\n" + "="*60)
    print("✅ Ethiopian data ready!")


if __name__ == "__main__":
    main()