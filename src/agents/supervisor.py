"""Supervisor agent for orchestrating the expense reimbursement workflow"""

from langgraph.types import Command
from ..types.state import ExpenseState

def supervisor_agent(state: ExpenseState) -> Command:
    """Central supervisor that routes to specialist agents"""
    
    print("=== SUPERVISOR DECISION MAKING ===")
    print(f"OCR Complete: {state.get('ocr_complete', False)}")
    print(f"Country Identified: {state.get('country_identified', False)}")
    print(f"Department Confirmed: {state.get('department_confirmed', False)}")
    print(f"Needs Clarification: {state.get('needs_clarification', False)}")
    print(f"Rules Applied: {state.get('rules_applied', False)}")
    print(f"Policy Violation: {state.get('policy_violation', False)}")
    print(f"Approval Determined: {state.get('approval_determined', False)}")

    # Determine next agent based on workflow state
    if not state.get("ocr_complete", False):
        next_agent = "receipt_processor"
        print("Routing to: RECEIPT_PROCESSOR (OCR needed)")
    elif not state.get("country_identified", False):
        next_agent = "location_analyst"
        print("Routing to: LOCATION_ANALYST (country identification)")
    elif not state.get("department_confirmed", False):
        next_agent = "classification"
        print("Routing to: CLASSIFICATION (department/purpose analysis)")
    elif state.get("needs_clarification", False):
        next_agent = "hitl"
        print("Routing to: HITL (human clarification needed)")
    elif not state.get("rules_applied", False):
        next_agent = "policy_engine"
        print("Routing to: POLICY_ENGINE (apply business rules)")
    elif state.get("policy_violation", False):
        next_agent = "exception_handler"
        print("Routing to: EXCEPTION_HANDLER (policy violation)")
    elif not state.get("approval_determined", False):
        next_agent = "approval_router"
        print("Routing to: APPROVAL_ROUTER (determine approval)")
    else:
        next_agent = "finalize"
        print("Routing to: FINALIZE (complete workflow)")

    state['current_agent'] = next_agent
    print(f"Current agent set to: {next_agent}")
    print("=== SUPERVISOR COMPLETE ===\n")
    return Command(goto=next_agent, update=state)