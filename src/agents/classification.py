"""Classification Agent - Classifies expense purpose and department"""

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command
from ..types.state import ExpenseState
from ..utils.helpers import extract_json_from_llm_response
from ..config.settings import LLM_MODEL, LLM_BASE_URL, LLM_DEFAULT_HEADERS, OPENROUTER_API_KEY, CLASSIFICATION_CONFIDENCE_THRESHOLD
from langchain_openai import ChatOpenAI

# Initialize LLM
llm = ChatOpenAI(
    model=LLM_MODEL,
    base_url=LLM_BASE_URL,
    api_key=OPENROUTER_API_KEY,
    default_headers=LLM_DEFAULT_HEADERS
)

def classification_agent_node(state: ExpenseState) -> Command:
    """Classify expense purpose and department"""
    prompt = f"""
    Analyze this expense:
    Dropoff: {state.get('dropoff_location', '')}
    Date: {state.get('expense_date', '')}
    Amount: {state.get('amount', '')}

    Infer department and purpose. Confidence 0-100.
    If confidence < {CLASSIFICATION_CONFIDENCE_THRESHOLD}, provide questions.

    Respond in JSON: {{"department": "...", "purpose": "...", "confidence": 0, "questions": []}}
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    parsed = extract_json_from_llm_response(response.content)
    state.update({
        "department": parsed["department"],
        "purpose": parsed["purpose"],
        "classification_confidence": parsed["confidence"]
    })

    if parsed["confidence"] < CLASSIFICATION_CONFIDENCE_THRESHOLD:
        state["needs_clarification"] = True
        state["clarification_questions"] = parsed["questions"]
        state["messages"].append(AIMessage(content=f"Classified: Department {parsed['department']}, Purpose {parsed['purpose']} (Confidence: {parsed['confidence']}%) - Need clarification"))
        return Command(goto="hitl", update=state)
    else:
        state["department_confirmed"] = True
        state["messages"].append(AIMessage(content=f"Classified: Department {parsed['department']}, Purpose {parsed['purpose']} (Confidence: {parsed['confidence']}%)"))
        return Command(goto="supervisor", update=state)