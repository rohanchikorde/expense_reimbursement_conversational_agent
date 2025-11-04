"""Supervisor agent for orchestrating the expense reimbursement workflow"""

from langgraph.types import Command
from ..types.state import ExpenseState

def supervisor_agent(state: ExpenseState) -> Command:
    """Central supervisor that routes to specialist agents"""

    # Determine next agent based on workflow state
    if not state.get("ocr_complete", False):
        next_agent = "receipt_processor"
    elif not state.get("country_identified", False):
        next_agent = "location_analyst"
    elif not state.get("department_confirmed", False):
        next_agent = "classification"
    elif state.get("needs_clarification", False):
        next_agent = "hitl"
    elif not state.get("rules_applied", False):
        next_agent = "policy_engine"
    elif state.get("policy_violation", False):
        next_agent = "exception_handler"
    elif not state.get("approval_determined", False):
        next_agent = "approval_router"
    else:
        next_agent = "finalize"

    state['current_agent'] = next_agent
    return Command(goto=next_agent, update=state)