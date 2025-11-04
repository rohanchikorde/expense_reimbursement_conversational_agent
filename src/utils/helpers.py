"""Utility functions for the expense reimbursement system"""

import json
from typing import Dict, Any, Optional
from langchain_core.messages import AIMessage, HumanMessage
from ..types.state import ExpenseState

def create_llm_response_parser():
    """Create a parser for LLM JSON responses"""
    def parse_json_response(response_text: str) -> Dict[str, Any]:
        """Parse JSON response from LLM, handling potential formatting issues"""
        try:
            # Try to parse as-is first
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1).strip())
                except json.JSONDecodeError:
                    pass

            # Try to find JSON-like content
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass

            # Return empty dict as fallback
            return {}

    return parse_json_response

def format_agent_message(content: str, agent_name: str = "Agent") -> AIMessage:
    """Format a message from an agent"""
    return AIMessage(content=f"[{agent_name}] {content}")

def validate_expense_data(state: ExpenseState) -> bool:
    """Validate that essential expense data is present"""
    required_fields = ['amount', 'expense_date', 'merchant']
    return all(state.get(field) is not None for field in required_fields)

def calculate_approval_threshold(expense_date: str) -> float:
    """Calculate the approval threshold based on expense date"""
    from ..config.settings import RULE_CHANGE_DATE, OLD_RULE_THRESHOLD, NEW_RULE_THRESHOLD

    if expense_date < RULE_CHANGE_DATE:
        return OLD_RULE_THRESHOLD
    else:
        return NEW_RULE_THRESHOLD

def determine_approval_status(amount: float, threshold: float) -> str:
    """Determine if expense requires approval based on amount and threshold"""
    if amount <= threshold:
        return "auto_approved"
    else:
        return "requires_manager"

def extract_json_from_llm_response(response_content: str) -> Dict[str, Any]:
    """Extract JSON from LLM response, handling various formats"""
    parser = create_llm_response_parser()
    return parser(response_content)