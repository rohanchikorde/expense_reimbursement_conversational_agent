"""Receipt Processor Agent - Handles OCR and data extraction from receipts"""

import pytesseract
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command
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

def receipt_processor_agent_node(state: ExpenseState) -> Command:
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
        info = extract_json_from_llm_response(response.content)
        state.update(info)
        state["messages"].append(AIMessage(content=f"Extracted from receipt: Amount {state['amount']} {state['currency']}, Date {state['expense_date']}, Merchant {state['merchant']}"))

    return Command(goto="supervisor", update=state)