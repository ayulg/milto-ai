"""Pytest configuration - add project root to Python path"""
import sys
from pathlib import Path

# This file is at backend/tests/conftest.py
# Project root (backend/) is at ../ (parent of tests/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Add backend/ to sys.path
sys.path.insert(0, str(PROJECT_ROOT))
