"""HITL (Human-in-the-Loop) Agent - Handles interactive conversations for clarification"""

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command, interrupt
from ..types.state import ExpenseState
from ..utils.helpers import extract_json_from_llm_response
from ..config.settings import LLM_MODEL, LLM_BASE_URL, LLM_DEFAULT_HEADERS, OPENROUTER_API_KEY
from langchain_openai import ChatOpenAI

# Initialize LLM
llm = ChatOpenAI(
    model=LLM_MODEL,
    base_url=LLM_BASE_URL,
    api_key=OPENROUTER_API_KEY,
    default_headers=LLM_DEFAULT_HEADERS
)

def hitl_agent_node(state: ExpenseState) -> Command:
    """Handle user clarification"""
    questions = state["clarification_questions"]
    question_text = "\n".join(questions)
    user_response = interrupt(question_text)

    # Parse response
    parse_prompt = f"User asked: {question_text}\nUser said: {user_response}\nExtract department and purpose."
    response = llm.invoke([HumanMessage(content=parse_prompt)])
    parsed = extract_json_from_llm_response(response.content)
    state.update({
        "department": parsed.get("department", state.get("department")),
        "purpose": parsed.get("purpose", state.get("purpose")),
        "needs_clarification": False,
        "department_confirmed": True,
        "user_provided_context": user_response
    })
    return Command(goto="supervisor", update=state)