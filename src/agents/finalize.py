"""Finalize Agent - Completes expense submission"""

from langchain_core.messages import AIMessage
from langgraph.types import Command
from ..types.state import ExpenseState

def finalize_agent_node(state: ExpenseState) -> Command:
    """Finalize"""
    # Stub
    state["messages"].append(AIMessage(content="Expense submitted successfully."))
    return Command(goto="finalize", update=state)