"""Exception Handler Agent - Manages policy violations and edge cases"""

from langgraph.types import Command
from ..types.state import ExpenseState

def exception_handler_agent_node(state: ExpenseState) -> Command:
    """Handle exceptions"""
    # Stub: assume no violation
    state["policy_violation"] = False
    return Command(goto="supervisor", update=state)