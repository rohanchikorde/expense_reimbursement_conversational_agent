#!/usr/bin/env python3
"""Test the fancy receipt with the full expense reimbursement workflow"""

import sys
import os
sys.path.append('src')

from PIL import Image
import pytesseract
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from src.workflow import expense_agent_system
from src.types.state import ExpenseState
from src.utils.helpers import extract_json_from_llm_response
from src.config.settings import LLM_MODEL, LLM_BASE_URL, LLM_DEFAULT_HEADERS, OPENROUTER_API_KEY

# Configure pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Initialize LLM
llm = ChatOpenAI(
    model=LLM_MODEL,
    base_url=LLM_BASE_URL,
    api_key=OPENROUTER_API_KEY,
    default_headers=LLM_DEFAULT_HEADERS
)

def test_fancy_receipt():
    """Test the fancy receipt with OCR and workflow"""

    receipt_path = "sample_fancy_receipt.png"
    if not os.path.exists(receipt_path):
        print(f"Error: Receipt not found: {receipt_path}")
        return

    print("=== TESTING FANCY RECEIPT ===")
    print(f"Loading receipt: {receipt_path}")

    # Load and test OCR
    receipt_image = Image.open(receipt_path)
    print(f"Image loaded: {receipt_image.size}")

    print("\n=== OCR PROCESSING ===")
    try:
        ocr_text = pytesseract.image_to_string(receipt_image)
        print("OCR SUCCESSFUL!")
        print(f"Text length: {len(ocr_text)} characters")
        print("\n--- OCR TEXT ---")
        print(ocr_text)
        print("--- END OCR TEXT ---\n")

        # Test LLM extraction
        print("=== LLM DATA EXTRACTION ===")
        prompt = f"""
        Extract from this Uber receipt text:
        - Amount (total fare as float)
        - Currency (str, default "USD")
        - Expense date (YYYY-MM-DD format)
        - Merchant (str, should be "Uber")
        - Pickup location (str)
        - Dropoff location (str)

        Receipt text: {ocr_text}

        Respond in JSON format with these exact keys.
        """

        response = llm.invoke([HumanMessage(content=prompt)])
        print(f"LLM response: {response.content}")

        extracted_data = extract_json_from_llm_response(response.content)
        print(f"Extracted data: {extracted_data}")

        # Test full workflow
        print("\n=== FULL WORKFLOW TEST ===")
        initial_state = ExpenseState(
            # Don't include receipt_image in initial state to avoid serialization issues
            # The receipt processor will handle OCR separately in this test
            ocr_text=ocr_text,  # Pre-extracted OCR text
            ocr_complete=True,  # Mark as already processed
            amount=None,
            currency=None,
            expense_date=None,
            merchant=None,
            pickup_location=None,
            dropoff_location=None,
            country=None,
            city=None,
            country_identified=False,
            department=None,
            purpose=None,
            classification_confidence=None,
            department_confirmed=False,
            needs_clarification=False,
            clarification_questions=[],
            user_provided_context=None,
            rules_applied=False,
            applied_rule=None,
            requires_manager_approval=None,
            approval_status=None,
            policy_violation=False,
            violations=[],
            current_agent=None,
            messages=[],
            employee_id="user_123",
            approval_determined=False
        )

        config = {"configurable": {"thread_id": "test_fancy_receipt"}}

        print("Starting workflow...")
        result = expense_agent_system.invoke(initial_state, config)
        print("Workflow completed!")

        # Check final state
        final_state = expense_agent_system.get_state(config).values
        print("\n=== FINAL RESULTS ===")
        print(f"Amount: {final_state.get('amount', 'N/A')}")
        print(f"Currency: {final_state.get('currency', 'N/A')}")
        print(f"Date: {final_state.get('expense_date', 'N/A')}")
        print(f"Merchant: {final_state.get('merchant', 'N/A')}")
        print(f"Pickup: {final_state.get('pickup_location', 'N/A')}")
        print(f"Dropoff: {final_state.get('dropoff_location', 'N/A')}")
        print(f"Country: {final_state.get('country', 'N/A')}")
        print(f"Department: {final_state.get('department', 'N/A')}")
        print(f"Purpose: {final_state.get('purpose', 'N/A')}")
        print(f"Approval Status: {final_state.get('approval_status', 'N/A')}")
        print(f"Requires Manager Approval: {final_state.get('requires_manager_approval', 'N/A')}")

        print(f"\nMessages: {len(final_state.get('messages', []))}")
        for i, msg in enumerate(final_state.get('messages', [])):
            print(f"  {i+1}. {type(msg).__name__}: {msg.content}")

        print("\n=== TEST COMPLETED SUCCESSFULLY ===")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fancy_receipt()