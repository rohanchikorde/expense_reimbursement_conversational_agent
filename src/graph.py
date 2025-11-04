from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from typing import TypedDict, Optional, Literal, List, Dict, Any
import pytesseract
from PIL import Image
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Set OpenRouter API key
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found in .env file")

llm = ChatOpenAI(
    model="z-ai/glm-4.5-air:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    default_headers={
        "HTTP-Referer": "http://localhost",  # Optional
        "X-Title": "Expense Reimbursement Agent",  # Optional
    }
)

# Define state schema
class ExpenseState(TypedDict):
    # Receipt data
    receipt_image: Optional[Image.Image]
    ocr_text: Optional[str]
    ocr_complete: bool
    
    # Extracted fields
    amount: Optional[float]
    currency: Optional[str]
    expense_date: Optional[str]
    merchant: Optional[str]
    pickup_location: Optional[str]
    dropoff_location: Optional[str]
    
    # Location analysis
    country: Optional[str]
    city: Optional[str]
    country_identified: bool
    
    # Classification
    department: Optional[str]
    purpose: Optional[str]
    classification_confidence: Optional[float]
    department_confirmed: bool
    
    # HITL
    needs_clarification: bool
    clarification_questions: List[str]
    user_provided_context: Optional[str]
    
    # Policy
    rules_applied: bool
    applied_rule: Optional[Dict]
    requires_manager_approval: Optional[bool]
    approval_status: Optional[Literal["pending", "auto_approved", "requires_manager"]]
    
    # Exceptions
    policy_violation: bool
    violations: List[Dict]
    
    # Workflow control
    current_agent: Optional[str]
    messages: List[Dict]
    employee_id: Optional[str]
    approval_determined: bool

# Supervisor routing function
def supervisor_agent(state: ExpenseState):
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

# Receipt Processor Agent
def receipt_processor_agent_node(state: ExpenseState):
    """Extract structured data from receipt"""
    if state["receipt_image"]:
        # Use pytesseract for text extraction
        text = pytesseract.image_to_string(state["receipt_image"])
        state["ocr_text"] = text
        state["ocr_complete"] = True
        
        # Use LLM to extract fields
        prompt = f"""
        Extract from the receipt text:
        - Amount (float)
        - Currency (str)
        - Expense date (YYYY-MM-DD)
        - Merchant (str)
        - Pickup location (str)
        - Dropoff location (str)
        
        Text: {text}
        
        Respond in JSON format.
        """
        response = llm.invoke([HumanMessage(content=prompt)])
        info = json.loads(response.content.strip())
        state.update(info)
        state["messages"].append(AIMessage(content=f"Extracted from receipt: Amount {state['amount']} {state['currency']}, Date {state['expense_date']}, Merchant {state['merchant']}"))
    
    return Command(goto="supervisor", update=state)

# Location Analyst Agent
def location_analyst_agent_node(state: ExpenseState):
    """Determine country from location data"""
    locations = f"{state.get('pickup_location', '')} {state.get('dropoff_location', '')}"
    prompt = f"Identify the country from these locations: {locations}. Respond with country name."
    response = llm.invoke([HumanMessage(content=prompt)])
    country = response.content.strip()
    state["country"] = country
    state["country_identified"] = True
    state["messages"].append(AIMessage(content=f"Identified country: {country}"))
    return Command(goto="supervisor", update=state)

# Classification Agent
def classification_agent_node(state: ExpenseState):
    """Classify expense purpose and department"""
    prompt = f"""
    Analyze this expense:
    Dropoff: {state.get('dropoff_location', '')}
    Date: {state.get('expense_date', '')}
    Amount: {state.get('amount', '')}
    
    Infer department and purpose. Confidence 0-100.
    If confidence < 90, provide questions.
    
    Respond in JSON: {{"department": "...", "purpose": "...", "confidence": 0, "questions": []}}
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    parsed = json.loads(response.content.strip())
    state.update({
        "department": parsed["department"],
        "purpose": parsed["purpose"],
        "classification_confidence": parsed["confidence"]
    })
    
    if parsed["confidence"] < 90:
        state["needs_clarification"] = True
        state["clarification_questions"] = parsed["questions"]
        state["messages"].append(AIMessage(content=f"Classified: Department {parsed['department']}, Purpose {parsed['purpose']} (Confidence: {parsed['confidence']}%) - Need clarification"))
        return Command(goto="hitl", update=state)
    else:
        state["department_confirmed"] = True
        state["messages"].append(AIMessage(content=f"Classified: Department {parsed['department']}, Purpose {parsed['purpose']} (Confidence: {parsed['confidence']}%)"))
        return Command(goto="supervisor", update=state)

# HITL Agent
def hitl_agent_node(state: ExpenseState):
    """Handle user clarification"""
    questions = state["clarification_questions"]
    question_text = "\n".join(questions)
    user_response = interrupt(question_text)
    
    # Parse response
    parse_prompt = f"User asked: {question_text}\nUser said: {user_response}\nExtract department and purpose."
    response = llm.invoke([HumanMessage(content=parse_prompt)])
    parsed = json.loads(response.content.strip())
    state.update({
        "department": parsed.get("department", state.get("department")),
        "purpose": parsed.get("purpose", state.get("purpose")),
        "needs_clarification": False,
        "department_confirmed": True,
        "user_provided_context": user_response
    })
    return Command(goto="supervisor", update=state)

# Policy Engine Agent
def policy_engine_agent_node(state: ExpenseState):
    """Apply business rules"""
    date = state.get("expense_date", "")
    amount = state.get("amount", 0)
    new_rule_date = "2024-01-01"
    if date < new_rule_date:
        requires = amount >= 50
    else:
        requires = amount >= 75
    state.update({
        "rules_applied": True,
        "requires_manager_approval": requires,
        "approval_status": "requires_manager" if requires else "auto_approved",
        "approval_determined": True
    })
    status = "requires manager approval" if requires else "auto-approved"
    state["messages"].append(AIMessage(content=f"Applied rules: {status}"))
    return Command(goto="supervisor", update=state)

# Stub agents
def exception_handler_agent_node(state: ExpenseState):
    """Handle exceptions"""
    # Stub: assume no violation
    state["policy_violation"] = False
    return Command(goto="supervisor", update=state)

def approval_router_agent_node(state: ExpenseState):
    """Route approval"""
    # Stub
    return Command(goto="supervisor", update=state)

def finalize_agent_node(state: ExpenseState):
    """Finalize"""
    # Stub
    state["messages"].append(AIMessage(content="Expense submitted successfully."))
    return Command(goto="finalize", update=state)

# Build the multi-agent workflow graph
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