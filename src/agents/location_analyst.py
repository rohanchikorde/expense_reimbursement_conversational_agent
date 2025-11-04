"""Location Analyst Agent - Determines country and geographic context"""

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command
from ..types.state import ExpenseState
from ..config.settings import LLM_MODEL, LLM_BASE_URL, LLM_DEFAULT_HEADERS, OPENROUTER_API_KEY
from langchain_openai import ChatOpenAI

# Initialize LLM
llm = ChatOpenAI(
    model=LLM_MODEL,
    base_url=LLM_BASE_URL,
    api_key=OPENROUTER_API_KEY,
    default_headers=LLM_DEFAULT_HEADERS
)

def location_analyst_agent_node(state: ExpenseState) -> Command:
    """Determine country from location data"""
    locations = f"{state.get('pickup_location', '')} {state.get('dropoff_location', '')}"
    prompt = f"Identify the country from these locations: {locations}. Respond with country name."
    response = llm.invoke([HumanMessage(content=prompt)])
    country = response.content.strip()
    state["country"] = country
    state["country_identified"] = True
    state["messages"].append(AIMessage(content=f"Identified country: {country}"))
    return Command(goto="supervisor", update=state)