"""Approval Router Agent - Determines final approval path"""

from langgraph.types import Command
from ..types.state import ExpenseState

def approval_router_agent_node(state: ExpenseState) -> Command:
    """Route approval"""
    # Stub: just pass through
    return Command(goto="supervisor", update=state)