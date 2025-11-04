# Expense Reimbursement Conversational Agent

This is a conversational AI agent built with LangGraph and Streamlit to handle Uber/Lyft expense reimbursements. It analyzes uploaded receipts to extract relevant information and applies company rules to determine if manager approval is needed.

## Features

- Conversational UI for uploading receipts
- OCR text extraction from receipt images
- LLM-based analysis to extract date, amount, country, and purpose
- Human-in-the-Loop (HITL) for unclear purposes
- Rule-based approval decision:
  - Expenses < $50: No approval needed (before 2024-01-01)
  - Expenses < $75: No approval needed (after 2024-01-01)

## Setup

1. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set OpenRouter API key in `.env`:
   ```
   OPENROUTER_API_KEY=your-api-key
   ```

## Running

```
streamlit run app.py
```

Upload a receipt image, and follow the conversation.

## Project Structure

```
src/
├── __init__.py
├── agents/                 # Individual agent modules
│   ├── __init__.py
│   ├── supervisor.py       # Orchestrates workflow
│   ├── receipt_processor.py # OCR and data extraction
│   ├── location_analyst.py  # Country identification
│   ├── classification.py    # Department/purpose classification
│   ├── hitl.py             # Human-in-the-loop interactions
│   ├── policy_engine.py    # Business rule application
│   ├── exception_handler.py # Policy violations
│   ├── approval_router.py  # Approval routing
│   └── finalize.py         # Submission completion
├── config/                 # Configuration settings
│   ├── __init__.py
│   └── settings.py         # API keys, thresholds, constants
├── types/                  # Type definitions
│   ├── __init__.py
│   └── state.py            # ExpenseState schema
├── utils/                  # Utility functions
│   ├── __init__.py
│   └── helpers.py          # Helper functions
└── workflow.py             # Main workflow orchestration

app.py                      # Streamlit UI
requirements.txt            # Python dependencies
.env                        # Environment variables (API keys)
.gitignore                  # Git ignore rules
README.md                   # This file
```