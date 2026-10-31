# Milto AI
### Adaptive AI-Powered Career Guidance Platform

Milto AI is an intelligent career exploration and personal development platform that helps people understand their strengths, discover career opportunities, and make informed career decisions.

## Overview

Milto AI combines personality assessment, machine learning, semantic career search, and generative AI to deliver personalized career guidance.

The platform brings together career discovery, assessment results, AI-powered conversations, and personal development tools in one application.

## Key Features

- **Personality Assessment:** Uses RIASEC and Big Five concepts to explore interests and personality traits.
- **AI Career Recommendations:** Helps users discover career paths using assessment results and machine learning.
- **Career Discovery:** Supports semantic search across more than 4,000 career records.
- **AI Career Coach:** Provides conversational career guidance through the Groq API.
- **Career Transition Support:** Helps users explore alternative career paths.
- **Personal Development:** Supports structured personal growth and skill development.
- **Ethiopian Career Context:** Includes locally relevant career, education, and university information.

## Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React 19, Vite, Tailwind CSS |
| Backend | Python 3.11, Flask |
| Database | SQLite |
| AI Integration | Groq API |
| Machine Learning | PyTorch, scikit-learn |
| Semantic Search | Sentence Transformers, FAISS |
| Testing | pytest |
| Version Control | Git and GitHub |
| CI | GitHub Actions |

## Project Structure

```text
milto-ai/
├── backend/
│   ├── data/
│   ├── models/
│   ├── modules/
│   ├── scripts/
│   ├── tests/
│   ├── app.py
│   ├── db.py
│   ├── engine.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── .github/
│   └── workflows/
└── README.md
