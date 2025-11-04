"""Configuration settings for the expense reimbursement system"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env file")

# LLM Configuration
LLM_MODEL = "z-ai/glm-4.5-air:free"
LLM_BASE_URL = "https://openrouter.ai/api/v1"
LLM_DEFAULT_HEADERS = {
    "HTTP-Referer": "http://localhost",
    "X-Title": "Expense Reimbursement Agent",
}

# Business Rules Configuration
RULE_CHANGE_DATE = "2024-01-01"  # Date when approval rules changed
OLD_RULE_THRESHOLD = 50  # Amount threshold before rule change
NEW_RULE_THRESHOLD = 75  # Amount threshold after rule change

# Agent Configuration
CLASSIFICATION_CONFIDENCE_THRESHOLD = 90  # Minimum confidence for auto-classification

# Workflow Configuration
DEFAULT_EMPLOYEE_ID = "user_123"

# UI Configuration
STREAMLIT_TITLE = "Expense Reimbursement Conversational Agent"