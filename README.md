# Milto AI - Adaptive Career Guidance Platform

An AI-powered career exploration and personal development system for Ethiopian university students.

## Overview

Milto AI combines psychological assessment (RIASEC + Big Five), machine learning, and large language models to help students discover, test, and transition into careers that fit them.

## Key Features

- **10-Level Personality Analysis**: Deep assessment of interests, skills, values, and personality.
- **AI Career Matching**: ML-powered ranking of 4,055 careers from ESCO + O*NET.
- **Ethiopian Context**: Local universities, salary data, and job market insights.
- **Career Bridge**: 4-phase transition plans for switching careers.
- **Personal Development**: 12-week plans to build specific skills or traits.
- **AI Coach**: A Groq-powered LLM assistant for personalized guidance.

## Tech Stack

- **Frontend**: React 18 + Vite + Tailwind CSS
- **Backend**: Python 3.11 + Flask + Waitress
- **Database**: SQLite (PostgreSQL ready)
- **AI**: Groq API (llama-3.3-70b-versatile)
- **ML/NLP**: scikit-learn, sentence-transformers, FAISS
- **CI/CD**: GitHub Actions
- **Testing**: pytest (12 tests passing)

## How to Run Locally

### Backend
1. cd backend
2. python -m venv .venv
3. .venv\Scripts\activate
4. pip install -r requirements.txt
5. waitress-serve --port=5000 app:app

### Frontend
1. cd frontend
2. npm install
3. npm run dev

### Environment Variables

Create a .env file in backend/ with:

ANTHROPIC_API_KEY=your_groq_api_key
MILTO_AI_MODEL=llama-3.3-70b-versatile
MILTO_SECRET_KEY=your_secret

## Testing

cd backend
pytest

## Author

Ayantu Legesse
GitHub: https://github.com/ayulg

## License

MIT
