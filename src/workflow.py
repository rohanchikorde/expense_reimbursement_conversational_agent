"""Main workflow orchestration for the expense reimbursement system"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .types.state import ExpenseState
from .agents.supervisor import supervisor_agent
from .agents.receipt_processor import receipt_processor_agent_node
from .agents.location_analyst import location_analyst_agent_node
from .agents.classification import classification_agent_node
from .agents.hitl import hitl_agent_node
from .agents.policy_engine import policy_engine_agent_node
from .agents.exception_handler import exception_handler_agent_node
from .agents.approval_router import approval_router_agent_node
from .agents.finalize import finalize_agent_node

def build_expense_workflow():
    """Construct the complete agentic workflow"""

    workflow = StateGraph(ExpenseState)

    # Add supervisor as the orchestrator
    workflow.add_node("supervisor", supervisor_agent)

    # Add specialist agents
    workflow.add_node("receipt_processor", receipt_processor_agent_node)
    workflow.add_node("location_analyst", location_analyst_agent_node)
    workflow.add_node("classification", classification_agent_node)
    workflow.add_node("hitl", hitl_agent_node)
    workflow.add_node("policy_engine", policy_engine_agent_node)
    workflow.add_node("exception_handler", exception_handler_agent_node)
    workflow.add_node("approval_router", approval_router_agent_node)
    workflow.add_node("finalize", finalize_agent_node)

    # Define workflow edges
    workflow.add_edge(START, "supervisor")

    # Specialist agents hand back to supervisor
    workflow.add_edge("receipt_processor", "supervisor")
    workflow.add_edge("location_analyst", "supervisor")
    workflow.add_edge("policy_engine", "supervisor")
    workflow.add_edge("exception_handler", "supervisor")
    workflow.add_edge("approval_router", "supervisor")
    workflow.add_edge("finalize", END)

    # Compile with checkpointing for HITL interruptions
    memory = MemorySaver()
    return workflow.compile(
        checkpointer=memory,
        interrupt_before=["hitl"]  # Pause before HITL for user input
    )

# Create the application
expense_agent_system = build_expense_workflow()

print("=== WORKFLOW SYSTEM INITIALIZED ===")
print("Available agents: supervisor, receipt_processor, location_analyst, classification, hitl, policy_engine, exception_handler, approval_router, finalize")
print("Interrupt configured before: hitl")
print("=== READY FOR EXPENSE PROCESSING ===\n")