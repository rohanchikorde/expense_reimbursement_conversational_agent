"""Policy Engine Agent - Applies temporal business rules"""

from langchain_core.messages import AIMessage
from langgraph.types import Command
from ..types.state import ExpenseState
from ..utils.helpers import calculate_approval_threshold, determine_approval_status
from ..config.settings import RULE_CHANGE_DATE

def policy_engine_agent_node(state: ExpenseState) -> Command:
    """Apply business rules"""
    date = state.get("expense_date", "")
    amount = state.get("amount", 0)

    # Calculate threshold based on date
    threshold = calculate_approval_threshold(date)

    # Determine approval status
    approval_status = determine_approval_status(amount, threshold)

    state.update({
        "rules_applied": True,
        "requires_manager_approval": approval_status == "requires_manager",
        "approval_status": approval_status,
        "approval_determined": True
    })

    status_msg = "requires manager approval" if approval_status == "requires_manager" else "auto-approved"
    state["messages"].append(AIMessage(content=f"Applied rules: {status_msg}"))
    return Command(goto="supervisor", update=state)